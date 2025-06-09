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
    try:

        resume_data_dict = ResumeController().prepare_resume_data(resume = resume_data)
        template = env.get_template(TemplateEnum.IMAGINE.value)
        rendered_html = template.render(**resume_data_dict)

        #html_file_path = "outputs/rendered_resume.html"
        # with open(html_file_path, "w", encoding="utf-8") as html_file:
        #     html_file.write(rendered_html)

        pdf_file_path = "outputs/resume_output.pdf"
        HTML(string=rendered_html).write_pdf(pdf_file_path)
        
        # browser = await launch()
        # page = await browser.newPage()

        # await page.setContent(rendered_html)
        # await page.pdf({'path': pdf_file_path, 'format': 'A4'})
        # await browser.close()

        return FileResponse(
            pdf_file_path,
            media_type="application/pdf",
            filename="resume.pdf"
        )
    
    except Exception as e:
        logger.error(f"Error building resume: {str(e)}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                                              "signal" : ResponseSignal.RESUME_BUILT_FAILURE.value
                                              })
    
    finally:
        # Clean up temporary PDF file
        if os.path.exists("resume_output.pdf"):
            os.remove("resume_output.pdf")


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
    link_service: LinkService = Depends(get_link_service)
):
    """
    Generate a resume PDF based on the authenticated user's data.
    
    This endpoint retrieves all the user's information from the database,
    builds a resume schema, and generates a PDF file.
    """
    try:
        # Get user ID from the authenticated user
        user_id = current_user["_id"]
        username = current_user["first_name"] + " " + current_user["last_name"]
        
        # Retrieve all user data from various services
        user_profile = await user_profile_service.get_user_profile(user_id)
        if not user_profile:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"signal": "User profile not found. Please complete your profile first."}
            )
        
        # Get education, experiences, skills, languages, certifications, and links
        educations = await education_service.get_user_educations(user_id)
        
        # Get career experiences (non-volunteer)
        all_experiences = await experience_service.get_user_experiences(user_id)
        career_experiences = [exp for exp in all_experiences if not exp.is_volunteer]
        volunteering_experiences = [exp for exp in all_experiences if exp.is_volunteer]
        
        # Get skills (technical and soft)
        all_skills = await skill_service.get_user_skills(user_id)
        technical_skills = [skill for skill in all_skills if not skill.is_soft_skill]
        soft_skills = [skill for skill in all_skills if skill.is_soft_skill]
        
        languages = await language_service.get_user_languages(user_id)
        certifications = await certification_service.get_user_certifications(user_id)
        links = await link_service.get_user_links(user_id)
        
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
            certifications=certifications,
            languages=languages,
            personal_links=links,
            personal_projects=[]  # Add this line with empty list for now

        )
        
        # Prepare resume data for template
        resume_data_dict = ResumeController().prepare_resume_data(resume=resume_data)
        
        # Get template and render HTML
        template = env.get_template(template_name)
        rendered_html = template.render(**resume_data_dict)
        
        # Generate unique filename to avoid conflicts
        unique_id = uuid.uuid4()
        pdf_file_path = f"outputs/resume_{unique_id}.pdf"
        
        # Ensure outputs directory exists
        os.makedirs("outputs", exist_ok=True)
        
        # Generate PDF
        HTML(string=rendered_html).write_pdf(pdf_file_path)
        
        return FileResponse(
            pdf_file_path,
            media_type="application/pdf",
            filename=f"resume_{username}.pdf",
            background=BackgroundTask(remove_file, pdf_file_path)        )
    
    except Exception as e:
        logger.error(f"Error generating resume: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, 
            content={"signal": ResponseSignal.RESUME_BUILT_FAILURE.value}
        )
            


