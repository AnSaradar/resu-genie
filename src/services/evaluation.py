import json
import logging
from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException, Depends
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

from .base import BaseService
from services.user_profile import UserProfileService
from services.experience import ExperienceService  
from services.education import EducationService
from schemas.evaluation import Evaluation, CompleteEvaluation
from dto.evaluation import EvaluationResponse, CompleteEvaluationResponse
from enums import DataBaseCollectionNames, ResponseSignal, EvaluationArea
from dependencies import get_db_client

class EvaluationService(BaseService):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.evaluations_collection = self.db_client[DataBaseCollectionNames.EVALUATIONS.value]
        self.complete_evaluations_collection = self.db_client[DataBaseCollectionNames.COMPLETE_EVALUATIONS.value]
        self.logger = logging.getLogger(__name__)

    async def evaluate_user_profile_area(self, user_id: ObjectId, llm_client, template_parser) -> EvaluationResponse:
        """Evaluate user profile area using LLM JSON response"""
        try:
            # Get user profile data
            profile_service = UserProfileService(self.db_client)
            user_profile = await profile_service.get_user_profile(user_id)
            
            if not user_profile:
                raise HTTPException(status_code=404, detail="User profile not found")

            # Prepare template variables
            template_vars = {
                'linkedin_url': user_profile.linkedin_url or "Not provided",
                'profile_summary': user_profile.profile_summary or "Not provided", 
                'current_position': user_profile.current_position or "Not provided",
                'work_field': user_profile.work_field.value if user_profile.work_field else "Not specified",
                'years_of_experience': user_profile.years_of_experience or "Not specified"
            }

            # Get evaluation prompt
            prompt = template_parser.get_template(
                group="evaluation",
                key="user_profile_evaluation_prompt", 
                vars=template_vars
            )

            # Generate JSON evaluation using LLM
            evaluation_data = llm_client.generate_json_response(
                prompt=prompt,
                temperature=0.3,
                max_output_tokens=500
            )

            # Validate required fields
            required_fields = ["score", "message", "suggestions"]
            for field in required_fields:
                if field not in evaluation_data:
                    raise ValueError(f"Missing required field '{field}' in LLM response")
            
            # Create evaluation response DTO
            return EvaluationResponse(
                score=evaluation_data["score"],
                message=evaluation_data["message"],
                suggestions=evaluation_data["suggestions"],
                status=evaluation_data["status"],
                evaluation_area=EvaluationArea.USER_PROFILE
            )

        except Exception as e:
            self.logger.error(f"Error evaluating user profile: {e}")
            raise HTTPException(status_code=400, detail=ResponseSignal.EVALUATION_ERROR.value)

    async def evaluate_experience_area(self, user_id: ObjectId, llm_client, template_parser) -> EvaluationResponse:
        """Evaluate experience area using LLM JSON response"""
        try:
            # Get user experiences
            experience_service = ExperienceService(self.db_client)
            experiences = await experience_service.get_user_experiences(user_id)

            # Format experiences for prompt
            experience_list = []
            for i, exp in enumerate(experiences, 1):
                exp_text = f"""
Experience {i}:
- Title: {exp.title}
- Company: {exp.company}
- Seniority: {exp.seniority_level.value}
- Duration: {exp.duration}
- Is Volunteer: {exp.is_volunteer}
- Description: {exp.description or "No description provided"}
"""
                experience_list.append(exp_text)

            template_vars = {
                'experience_list': "\n".join(experience_list) if experience_list else "No experiences provided"
            }

            # Get evaluation prompt
            prompt = template_parser.get_template(
                group="evaluation",
                key="experience_evaluation_prompt",
                vars=template_vars
            )

            # Generate JSON evaluation using LLM
            evaluation_data = llm_client.generate_json_response(
                prompt=prompt,
                temperature=0.3,
                max_output_tokens=500
            )

            # Validate required fields
            required_fields = ["score", "message", "suggestions"]
            for field in required_fields:
                if field not in evaluation_data:
                    raise ValueError(f"Missing required field '{field}' in LLM response")
            
            return EvaluationResponse(
                score=evaluation_data["score"],
                message=evaluation_data["message"],
                suggestions=evaluation_data["suggestions"],
                status=evaluation_data["status"],
                evaluation_area=EvaluationArea.EXPERIENCE
            )

        except Exception as e:
            self.logger.error(f"Error evaluating experiences: {e}")
            raise HTTPException(status_code=400, detail=ResponseSignal.EVALUATION_ERROR.value)

    async def evaluate_education_area(self, user_id: ObjectId, llm_client, template_parser) -> EvaluationResponse:
        """Evaluate education area using LLM JSON response"""
        try:
            # Get user educations
            education_service = EducationService(self.db_client)
            educations = await education_service.get_user_educations(user_id)

            # Format education for prompt
            education_list = []
            for i, edu in enumerate(educations, 1):
                edu_text = f"""
Education {i}:
- Institution: {edu.institution}
- Degree: {edu.degree.value}
- Field: {edu.field}
- Duration: {"Currently studying" if edu.currently_studying else f"{edu.start_date} to {edu.end_date}"}
- Description: {edu.description or "No description provided"}
"""
                education_list.append(edu_text)

            template_vars = {
                'education_list': "\n".join(education_list) if education_list else "No education provided"
            }

            # Get evaluation prompt
            prompt = template_parser.get_template(
                group="evaluation", 
                key="education_evaluation_prompt",
                vars=template_vars
            )

            # Generate JSON evaluation using LLM
            evaluation_data = llm_client.generate_json_response(
                prompt=prompt,
                temperature=0.3,
                max_output_tokens=500
            )

            # Validate required fields
            required_fields = ["score", "message", "suggestions"]
            for field in required_fields:
                if field not in evaluation_data:
                    raise ValueError(f"Missing required field '{field}' in LLM response")
            
            return EvaluationResponse(
                score=evaluation_data["score"],
                message=evaluation_data["message"],
                suggestions=evaluation_data["suggestions"],
                status=evaluation_data["status"],
                evaluation_area=EvaluationArea.EDUCATION
            )

        except Exception as e:
            self.logger.error(f"Error evaluating education: {e}")
            raise HTTPException(status_code=400, detail=ResponseSignal.EVALUATION_ERROR.value)

    async def evaluate_complete_profile(self, user_id: ObjectId, llm_client, template_parser) -> CompleteEvaluationResponse:
        """Evaluate complete user profile with all components"""
        try:
            # Get individual evaluations
            profile_eval = await self.evaluate_user_profile_area(user_id, llm_client, template_parser)
            experience_eval = await self.evaluate_experience_area(user_id, llm_client, template_parser) 
            education_eval = await self.evaluate_education_area(user_id, llm_client, template_parser)

            # Calculate overall score
            overall_score = (profile_eval.score + experience_eval.score + education_eval.score) / 3

            # Combine top suggestions
            all_suggestions = (profile_eval.suggestions + 
                             experience_eval.suggestions + 
                             education_eval.suggestions)
            
            # Get top 3 most critical suggestions
            #overall_suggestions = all_suggestions[:3]
            overall_suggestions = all_suggestions

            return CompleteEvaluationResponse(
                overall_score=round(overall_score, 1),
                user_profile_evaluation=profile_eval,
                experience_evaluation=experience_eval,
                education_evaluation=education_eval, 
                overall_suggestions=overall_suggestions
            )

        except Exception as e:
            self.logger.error(f"Error in complete profile evaluation: {e}")
            raise HTTPException(status_code=400, detail=ResponseSignal.EVALUATION_ERROR.value)

    async def get_evaluation_history(self, user_id: ObjectId, evaluation_area: Optional[EvaluationArea] = None) -> List[Evaluation]:
        """Get evaluation history for user"""
        try:
            query = {"user_id": user_id}
            if evaluation_area:
                query["evaluation_area"] = evaluation_area.value
                
            evaluations = await self.evaluations_collection.find(query).sort("created_at", -1).to_list(None)
            return [Evaluation(**eval) for eval in evaluations]
            
        except Exception as e:
            self.logger.error(f"Error getting evaluation history: {e}")
            raise HTTPException(status_code=400, detail=ResponseSignal.EVALUATION_HISTORY_ERROR.value)


def get_evaluation_service(db_client: AsyncIOMotorClient = Depends(get_db_client)):
    """Dependency function to get evaluation service"""
    return EvaluationService(db_client) 