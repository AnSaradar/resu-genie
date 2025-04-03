from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import logging
from fastapi.responses import JSONResponse
from bson import ObjectId
from enums import ResponseSignal
from services.experiance import ExperienceService, get_experience_service
from dto.experiance import ExperienceCreate, ExperienceUpdate, ExperienceResponse
from dependencies.auth import get_current_user
from controllers.BaseController import BaseController

logger = logging.getLogger(__name__)

experience_router = APIRouter(
    prefix="/api/v1/experience",
    tags=["api_v1", "experience"],
)

@experience_router.post("/add", response_model=List[ExperienceResponse])
async def add_experiences(
    experiences: List[ExperienceCreate],
    current_user: dict = Depends(get_current_user),
    experience_service: ExperienceService = Depends(get_experience_service)
):
    """Add multiple experiences for the authenticated user"""
    try:
        created_experiences = await experience_service.create_experiences(
            user_id=current_user["user_id"],
            experiences_data=experiences
        )
        
        experiences_data = BaseController().get_json_serializable_object(created_experiences)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "signal": ResponseSignal.EXPERIENCE_CREATE_SUCCESS.value,
                "experiences": experiences_data
            }
        )
    except Exception as e:
        logger.error(f"Error adding experiences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseSignal.EXPERIENCE_CREATE_ERROR.value
        )

@experience_router.put("/{experience_id}", response_model=ExperienceResponse)
async def update_experience(
    experience_id: str,
    update_data: ExperienceUpdate,
    current_user: dict = Depends(get_current_user),
    experience_service: ExperienceService = Depends(get_experience_service)
):
    """Update a specific experience entry"""
    try:
        updated_experience = await experience_service.update_experience(
            user_id=current_user["user_id"],
            experience_id=ObjectId(experience_id),
            update_data=update_data
        )
        
        experience_data = BaseController().get_json_serializable_object(updated_experience)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.EXPERIENCE_UPDATE_SUCCESS.value,
                "experience": experience_data
            }
        )
    except Exception as e:
        logger.error(f"Error updating experience: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseSignal.EXPERIENCE_UPDATE_ERROR.value
        )

@experience_router.delete("/{experience_id}")
async def delete_experience(
    experience_id: str,
    current_user: dict = Depends(get_current_user),
    experience_service: ExperienceService = Depends(get_experience_service)
):
    """Delete a specific experience entry"""
    try:
        await experience_service.delete_experience(
            user_id=current_user["user_id"],
            experience_id=ObjectId(experience_id)
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.EXPERIENCE_DELETE_SUCCESS.value
            }
        )
    except Exception as e:
        logger.error(f"Error deleting experience: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseSignal.EXPERIENCE_DELETE_ERROR.value
        )

@experience_router.get("/all", response_model=List[ExperienceResponse])
async def get_all_experiences(
    current_user: dict = Depends(get_current_user),
    experience_service: ExperienceService = Depends(get_experience_service)
):
    """Get all experiences for the authenticated user"""
    try:
        experiences = await experience_service.get_user_experiences(
            user_id=current_user["user_id"]
        )
        
        experiences_data = BaseController().get_json_serializable_object(experiences)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.EXPERIENCE_RETRIEVE_SUCCESS.value,
                "experiences": experiences_data
            }
        )
    except Exception as e:
        logger.error(f"Error retrieving experiences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseSignal.EXPERIENCE_RETRIEVE_ERROR.value
        )
