from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from bson import ObjectId
from services.education import EducationService, get_education_service
from dto.education import EducationCreate, EducationUpdate, EducationResponse
from dependencies import get_current_user
from schemas.user import User
from enums import ResponseSignal

education_router = APIRouter(
    prefix="/education",
    tags=["education"],
    responses={404: {"description": "Not found"}},
)

@education_router.post("/", response_model=List[EducationResponse], status_code=status.HTTP_201_CREATED)
async def create_educations(
    educations: List[EducationCreate],
    current_user: User = Depends(get_current_user),
    education_service: EducationService = Depends(get_education_service)
):
    """
    Create multiple education entries for the current user.
    """
    return await education_service.create_educations(
        user_id=current_user.id,
        educations_data=educations
    )

@education_router.get("/", response_model=List[EducationResponse])
async def get_user_educations(
    current_user: User = Depends(get_current_user),
    education_service: EducationService = Depends(get_education_service)
):
    """
    Get all education entries for the current user.
    """
    return await education_service.get_user_educations(user_id=current_user.id)

@education_router.get("/{education_id}", response_model=EducationResponse)
async def get_education(
    education_id: str,
    current_user: User = Depends(get_current_user),
    education_service: EducationService = Depends(get_education_service)
):
    """
    Get a specific education entry by ID.
    """
    try:
        obj_id = ObjectId(education_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid education ID format"
        )
        
    education = await education_service.get_education(
        user_id=current_user.id,
        education_id=obj_id
    )
    
    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignal.EDUCATION_NOT_FOUND.value
        )
        
    return education

@education_router.put("/{education_id}", response_model=EducationResponse)
async def update_education(
    education_id: str,
    update_data: EducationUpdate,
    current_user: User = Depends(get_current_user),
    education_service: EducationService = Depends(get_education_service)
):
    """
    Update a specific education entry by ID.
    """
    try:
        obj_id = ObjectId(education_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid education ID format"
        )
        
    updated_education = await education_service.update_education(
        user_id=current_user.id,
        education_id=obj_id,
        update_data=update_data
    )
    
    return updated_education

@education_router.delete("/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education(
    education_id: str,
    current_user: User = Depends(get_current_user),
    education_service: EducationService = Depends(get_education_service)
):
    """
    Delete a specific education entry by ID.
    """
    try:
        obj_id = ObjectId(education_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid education ID format"
        )
        
    result = await education_service.delete_education(
        user_id=current_user.id,
        education_id=obj_id
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignal.EDUCATION_NOT_FOUND.value
        )
