from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from bson import ObjectId
from services.skill import SkillService, get_skill_service
from dto.skill import SkillCreate, SkillUpdate, SkillResponse, SkillsGroupResponse
from dependencies.auth import get_current_user
from schemas.user import User
from enums import ResponseSignal
from controllers.BaseController import BaseController
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


skill_router = APIRouter(
    prefix="/api/v1/skill",
    tags=["api_v1", "skill"],
    responses={404: {"description": "Not found"}},
)

@skill_router.post("/", response_model=List[SkillResponse], status_code=status.HTTP_201_CREATED)
async def create_skills(
    skills: List[SkillCreate],
    current_user: User = Depends(get_current_user),
    skill_service: SkillService = Depends(get_skill_service)
):
    """
    Create multiple skill entries for the current user.
    """
    user_id = current_user["_id"]
    try:    
        created_skills = await skill_service.create_skills(
            user_id=user_id,
            skills_data=skills
        )
        skills_data = BaseController().get_json_serializable_object(created_skills)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "signal": ResponseSignal.SKILL_CREATE_SUCCESS.value,
                "skills": skills_data
            }
        )
    except Exception as e: 
        logger.error(f"Error in create_skills: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseSignal.SKILL_CREATE_ERROR.value
        )

@skill_router.get("/", response_model=List[SkillResponse])
async def get_user_skills(
    current_user: User = Depends(get_current_user),
    skill_service: SkillService = Depends(get_skill_service)
):
    """
    Get all skill entries for the current user.
    """
    user_id = current_user["_id"]
    try:
        user_skills = await skill_service.get_user_skills(user_id=user_id)
        skills_data = BaseController().get_json_serializable_object(user_skills)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.SKILL_RETRIEVE_SUCCESS.value,
                "skills": skills_data
            }
        )
    except Exception as e:
        logger.error(f"Error in get_user_skills: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseSignal.SKILL_RETRIEVE_ERROR.value
        )

@skill_router.get("/grouped", response_model=List[SkillsGroupResponse])
async def get_grouped_skills(
    current_user: User = Depends(get_current_user),
    skill_service: SkillService = Depends(get_skill_service)
):
    """
    Get all skills for the current user, grouped by proficiency level.
    """
    user_id = current_user["_id"]
    try:
        grouped_skills = await skill_service.group_skills_by_proficiency(user_id=user_id)
        grouped_skills_data = BaseController().get_json_serializable_object(grouped_skills)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
                content={
                "signal": ResponseSignal.SKILL_RETRIEVE_SUCCESS.value,
                "skills": grouped_skills_data
            }
        )
    except Exception as e:
        logger.error(f"Error in get_grouped_skills: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseSignal.SKILL_RETRIEVE_ERROR.value
        )


@skill_router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(
    skill_id: str,
    current_user: User = Depends(get_current_user),
    skill_service: SkillService = Depends(get_skill_service)
):
    """
    Get a specific skill entry by ID.
    """
    user_id = current_user["_id"]
    try:
        obj_id = ObjectId(skill_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid skill ID format"
        )
        
    skill = await skill_service.get_skill(
        user_id=user_id,
        skill_id=obj_id
    )
    skill_data = BaseController().get_json_serializable_object(skill)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.SKILL_RETRIEVE_SUCCESS.value,
            "skill": skill_data
        }
    )   

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignal.SKILL_NOT_FOUND.value
        )
        
    return skill

@skill_router.put("/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: str,
    update_data: SkillUpdate,
    current_user: User = Depends(get_current_user),
    skill_service: SkillService = Depends(get_skill_service)
):
    """
    Update a specific skill entry by ID.
    """
    user_id = current_user["_id"]
    try:
        obj_id = ObjectId(skill_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid skill ID format"
        )
        
    updated_skill = await skill_service.update_skill(
        user_id=user_id,
        skill_id=obj_id,
        update_data=update_data
    )
    skill_data = BaseController().get_json_serializable_object(updated_skill)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.SKILL_UPDATE_SUCCESS.value,
            "skill": skill_data
        }
    )

@skill_router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: str,
    current_user: User = Depends(get_current_user),
    skill_service: SkillService = Depends(get_skill_service)
):
    """
    Delete a specific skill entry by ID.
    """
    user_id = current_user["_id"]
    try:
        obj_id = ObjectId(skill_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid skill ID format"
        )
        
    result = await skill_service.delete_skill(
        user_id=user_id,
        skill_id=obj_id
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignal.SKILL_NOT_FOUND.value
        ) 
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content={
            "signal": ResponseSignal.SKILL_DELETE_SUCCESS.value
        }
    )