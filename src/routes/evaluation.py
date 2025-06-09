from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional
import logging
from fastapi.responses import JSONResponse

from services.evaluation import EvaluationService, get_evaluation_service
from dto.evaluation import EvaluationResponse, CompleteEvaluationResponse
from schemas.evaluation import Evaluation, EvaluationArea
from dependencies.auth import get_current_user
from controllers.BaseController import BaseController
from enums import ResponseSignal
from schemas.user import User

logger = logging.getLogger(__name__)

evaluation_router = APIRouter(
    prefix="/api/v1/evaluation",
    tags=["api_v1", "evaluation"],
)

@evaluation_router.post("/complete", response_model=CompleteEvaluationResponse)
async def evaluate_complete_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
    evaluation_service: EvaluationService = Depends(get_evaluation_service)
):
    """
    Evaluate complete user profile including profile, experiences, and education
    Returns comprehensive evaluation with overall score and individual component scores
    """
    try:
        user_id = current_user["_id"]
        
        # Get LLM components from app instance (initialized in main.py)
        llm_client = request.app.generation_client
        template_parser = request.app.template_parser
        
        evaluation_result = await evaluation_service.evaluate_complete_profile(
            user_id, llm_client, template_parser
        )
        
        evaluation_data = BaseController().get_json_serializable_object(evaluation_result)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.EVALUATION_SUCCESS.value,
                "evaluation": evaluation_data
            }
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error in complete profile evaluation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseSignal.EVALUATION_ERROR.value
        )

@evaluation_router.post("/area/{evaluation_area}", response_model=EvaluationResponse)
async def evaluate_profile_area(
    evaluation_area: EvaluationArea,
    request: Request,
    current_user: User = Depends(get_current_user),
    evaluation_service: EvaluationService = Depends(get_evaluation_service)
):
    """
    Evaluate specific area of user profile
    
    Available areas:
    - user_profile: Evaluate profile information, LinkedIn URL, summary, etc.
    - experience: Evaluate work experience entries
    - education: Evaluate education entries
    """
    try:
        user_id = current_user["_id"]
        
        # Get LLM components from app instance (initialized in main.py)
        llm_client = request.app.generation_client
        template_parser = request.app.template_parser
        
        if evaluation_area == EvaluationArea.USER_PROFILE:
            evaluation_result = await evaluation_service.evaluate_user_profile_area(
                user_id, llm_client, template_parser
            )
        elif evaluation_area == EvaluationArea.EXPERIENCE:
            evaluation_result = await evaluation_service.evaluate_experience_area(
                user_id, llm_client, template_parser
            )
        elif evaluation_area == EvaluationArea.EDUCATION:
            evaluation_result = await evaluation_service.evaluate_education_area(
                user_id, llm_client, template_parser
            )
        else:
            raise HTTPException(
                status_code=400, 
                detail="Invalid evaluation area. Use: user_profile, experience, or education"
            )

        # Optionally save the evaluation result
        # await evaluation_service.save_evaluation_result(user_id, evaluation_result)
        
        evaluation_data = BaseController().get_json_serializable_object(evaluation_result)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.EVALUATION_SUCCESS.value,
                "evaluation": evaluation_data
            }
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error evaluating {evaluation_area}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseSignal.EVALUATION_ERROR.value
        )

@evaluation_router.get("/history", response_model=List[Evaluation])
async def get_evaluation_history(
    evaluation_area: Optional[EvaluationArea] = None,
    current_user: User = Depends(get_current_user),
    evaluation_service: EvaluationService = Depends(get_evaluation_service)
):
    """
    Get evaluation history for the authenticated user
    Optionally filter by evaluation area
    """
    try:
        user_id = current_user["user_id"]
        
        evaluations = await evaluation_service.get_evaluation_history(
            user_id=user_id,
            evaluation_area=evaluation_area
        )
        
        evaluations_data = BaseController().get_json_serializable_object(evaluations)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.EVALUATION_HISTORY_SUCCESS.value,
                "evaluations": evaluations_data
            }
        )

    except Exception as e:
        logger.error(f"Error retrieving evaluation history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseSignal.EVALUATION_HISTORY_ERROR.value
        )

@evaluation_router.get("/areas", response_model=List[str])
async def get_evaluation_areas():
    """Get a list of all available evaluation areas"""
    return [area.value for area in EvaluationArea if area != EvaluationArea.COMPLETE] 