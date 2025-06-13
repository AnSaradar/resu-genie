from fastapi import FastAPI, APIRouter, Depends, status
from fastapi.responses import JSONResponse, FileResponse
from starlette.background import BackgroundTask
from core.config import get_settings, Settings
from enums import ResponseSignal, TemplateEnum
from schemas.resume import Resume
from controllers import ResumeController
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import logging
import os
from dependencies import get_current_user
from schemas.user import User
from services.user_profile import get_user_profile_service, UserProfileService
from services.education import get_education_service, EducationService
from services.experience import get_experience_service, ExperienceService
from services.skill import get_skill_service, SkillService
from services.language import get_language_service, LanguageService
from services.certification import get_certification_service, CertificationService
from services.link import get_link_service, LinkService
from services.personal_project import get_personal_project_service, PersonalProjectService
from bson import ObjectId
import uuid
from core.utils import remove_file

resume_router = APIRouter(
    prefix = "/api/v1/resume",
    tags = ["api_v1"]
)

logger = logging.getLogger(__name__)

# Initialize Jinja2 environment
env = Environment(loader=FileSystemLoader("resume_templates"))


@resume_router.post("/build")
async def build_resume(resume_data: Resume):
    """Build resume from provided data (no authentication required)."""
    try:
        # Validate resume data
        controller = ResumeController()
        validation_errors = controller.validate_resume_data(resume_data)
        
        if validation_errors:
            logger.warning(f"Resume build with validation warnings: {validation_errors}")
        
        # Prepare resume data for template
        resume_data_dict = controller.prepare_resume_data(resume=resume_data)
        
        # Get template and render HTML
        template = env.get_template(TemplateEnum.MOEY.value)
        rendered_html = template.render(**resume_data_dict)

        # Generate unique filename and ensure directory exists
        unique_id = uuid.uuid4()
        pdf_file_path = f"outputs/resume_build_{unique_id}.pdf"
        os.makedirs("outputs", exist_ok=True)
        
        # Generate PDF
        HTML(string=rendered_html).write_pdf(pdf_file_path)

        return FileResponse(
            pdf_file_path,
            media_type="application/pdf",
            filename="resume.pdf",
            background=BackgroundTask(remove_file, pdf_file_path)
        )
    
    except ValueError as ve:
        logger.error(f"Validation error building resume: {str(ve)}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            content={"signal": "Invalid resume data", "details": str(ve)}
        )
    except Exception as e:
        logger.error(f"Error building resume: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, 
            content={"signal": ResponseSignal.RESUME_BUILT_FAILURE.value}
        )


@resume_router.get("/generate")
async def generate_resume(
    template_name: str = TemplateEnum.IMAGINE.value,
    current_user: User = Depends(get_current_user),
    user_profile_service: UserProfileService = Depends(get_user_profile_service),
    education_service: EducationService = Depends(get_education_service),
    experience_service: ExperienceService = Depends(get_experience_service),
    skill_service: SkillService = Depends(get_skill_service),
    language_service: LanguageService = Depends(get_language_service),
    certification_service: CertificationService = Depends(get_certification_service),
    link_service: LinkService = Depends(get_link_service),
    personal_project_service: PersonalProjectService = Depends(get_personal_project_service)
):
    """Generate a resume PDF based on the authenticated user's data."""
    try:
        # Get user identification
        user_id = current_user["_id"]
        username = f"{current_user['first_name']} {current_user['last_name']}"
        
        logger.info(f"Generating resume for user {user_id}")
        
        # Validate template exists
        try:
            template = env.get_template(template_name)
        except Exception as e:
            logger.error(f"Template {template_name} not found: {e}")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"signal": f"Template {template_name} not found"}
            )
        
        # Retrieve all user data from various services
        user_profile = await user_profile_service.get_user_profile(user_id)
        if not user_profile:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"signal": "User profile not found. Please complete your profile first."}
            )
        
        # Fetch all user data in parallel for better performance
        logger.info("Fetching user data from services")
        
        educations = await education_service.get_user_educations(user_id)
        all_experiences = await experience_service.get_user_experiences(user_id)
        all_skills = await skill_service.get_user_skills(user_id)
        languages = await language_service.get_user_languages(user_id)
        certifications = await certification_service.get_user_certifications(user_id)
        links = await link_service.get_user_links(user_id)
        personal_projects = await personal_project_service.get_user_personal_projects(user_id)
        
        # Process and categorize data
        career_experiences = [exp for exp in all_experiences if not exp.is_volunteer]
        volunteering_experiences = [exp for exp in all_experiences if exp.is_volunteer]
        technical_skills = [skill for skill in all_skills if not skill.is_soft_skill]
        soft_skills = [skill for skill in all_skills if skill.is_soft_skill]
        
        # Log data statistics
        logger.info(f"Data summary - Experiences: {len(career_experiences)}, "
                   f"Volunteering: {len(volunteering_experiences)}, "
                   f"Education: {len(educations)}, "
                   f"Technical Skills: {len(technical_skills)}, "
                   f"Soft Skills: {len(soft_skills)}")
        
        # Build resume schema
        resume_data = Resume(
            id=ObjectId(),
            user_id=user_id,
            personal_info=user_profile,
            career_experiences=career_experiences,
            volunteering_experiences=volunteering_experiences,
            education=educations,
            technical_skills=technical_skills,
            soft_skills=soft_skills,
            certifications=certifications or [],
            languages=languages,
            personal_links=links or [],
            personal_projects=personal_projects or []
        )
        
        # Prepare resume data for template using improved controller
        controller = ResumeController()
        resume_data_dict = controller.prepare_resume_data(resume=resume_data, current_user=current_user)
        
        # Log template data for debugging
        logger.info(f"Template data prepared with {len(resume_data_dict)} fields")
        
        # Render HTML template
        rendered_html = template.render(**resume_data_dict)
        
        # Generate unique filename and ensure directory exists
        unique_id = uuid.uuid4()
        pdf_file_path = f"outputs/resume_{unique_id}.pdf"
        os.makedirs("outputs", exist_ok=True)
        
        # Generate PDF
        logger.info(f"Generating PDF: {pdf_file_path}")
        HTML(string=rendered_html).write_pdf(pdf_file_path)
        
        return FileResponse(
            pdf_file_path,
            media_type="application/pdf",
            filename=f"resume_{username.replace(' ', '_')}.pdf",
            background=BackgroundTask(remove_file, pdf_file_path)
        )
    
    except ValueError as ve:
        logger.error(f"Data validation error: {str(ve)}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"signal": "Resume data validation failed", "details": str(ve)}
        )
    except Exception as e:
        logger.error(f"Error generating resume: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content={"signal": ResponseSignal.RESUME_BUILT_FAILURE.value}
        )


@resume_router.get("/validate")
async def validate_user_resume_data(
    current_user: User = Depends(get_current_user),
    user_profile_service: UserProfileService = Depends(get_user_profile_service),
    education_service: EducationService = Depends(get_education_service),
    experience_service: ExperienceService = Depends(get_experience_service),
):
    """Validate if user has sufficient data to generate a quality resume."""
    try:
        user_id = current_user["_id"]
        
        # Check user profile
        user_profile = await user_profile_service.get_user_profile(user_id)
        educations = await education_service.get_user_educations(user_id)
        experiences = await experience_service.get_user_experiences(user_id)
        
        validation_result = {
            "can_generate_resume": True,
            "missing_data": [],
            "recommendations": []
        }
        
        # Check essential data
        if not user_profile:
            validation_result["missing_data"].append("User profile")
            validation_result["can_generate_resume"] = False
        
        if not experiences and not educations:
            validation_result["missing_data"].append("Either work experience or education")
            validation_result["can_generate_resume"] = False
        
        # Add recommendations for better resume
        if user_profile and not user_profile.profile_summary:
            validation_result["recommendations"].append("Add a professional summary")
        
        if not experiences:
            validation_result["recommendations"].append("Add work experience")
        
        if not educations:
            validation_result["recommendations"].append("Add education details")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=validation_result
        )
        
    except Exception as e:
        logger.error(f"Error validating resume data: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"signal": "Error validating resume data"}
        )


