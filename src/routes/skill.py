from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from bson import ObjectId
from services.skill import SkillService, get_skill_service
from dto.skill import SkillCreate, SkillUpdate, SkillResponse, SkillsGroupResponse
from dependencies.auth import get_current_user
from schemas.user import User
from enums import ResponseSignal

skill_router = APIRouter(
    prefix="/skills",
    tags=["skills"],
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
    return await skill_service.create_skills(
        user_id=current_user.id,
        skills_data=skills
    )

@skill_router.get("/", response_model=List[SkillResponse])
async def get_user_skills(
    current_user: User = Depends(get_current_user),
    skill_service: SkillService = Depends(get_skill_service)
):
    """
    Get all skill entries for the current user.
    """
    return await skill_service.get_user_skills(user_id=current_user.id)

@skill_router.get("/grouped", response_model=List[SkillsGroupResponse])
async def get_grouped_skills(
    current_user: User = Depends(get_current_user),
    skill_service: SkillService = Depends(get_skill_service)
):
    """
    Get all skills for the current user, grouped by proficiency level.
    """
    return await skill_service.group_skills_by_proficiency(user_id=current_user.id)

@skill_router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(
    skill_id: str,
    current_user: User = Depends(get_current_user),
    skill_service: SkillService = Depends(get_skill_service)
):
    """
    Get a specific skill entry by ID.
    """
    try:
        obj_id = ObjectId(skill_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid skill ID format"
        )
        
    skill = await skill_service.get_skill(
        user_id=current_user.id,
        skill_id=obj_id
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
    try:
        obj_id = ObjectId(skill_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid skill ID format"
        )
        
    updated_skill = await skill_service.update_skill(
        user_id=current_user.id,
        skill_id=obj_id,
        update_data=update_data
    )
    
    return updated_skill

@skill_router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: str,
    current_user: User = Depends(get_current_user),
    skill_service: SkillService = Depends(get_skill_service)
):
    """
    Delete a specific skill entry by ID.
    """
    try:
        obj_id = ObjectId(skill_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid skill ID format"
        )
        
    result = await skill_service.delete_skill(
        user_id=current_user.id,
        skill_id=obj_id
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignal.SKILL_NOT_FOUND.value
        ) 