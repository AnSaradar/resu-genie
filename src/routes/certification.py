from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from bson import ObjectId
from services.certification import CertificationService, get_certification_service
from dto.certification import CertificationCreate, CertificationUpdate, CertificationResponse
from dependencies import get_current_user
from schemas.user import User
from enums import ResponseSignal

certification_router = APIRouter(
    prefix="/certifications",
    tags=["certifications"],
    responses={404: {"description": "Not found"}},
)

@certification_router.post("/", response_model=List[CertificationResponse], status_code=status.HTTP_201_CREATED)
async def create_certifications(
    certifications: List[CertificationCreate],
    current_user: User = Depends(get_current_user),
    certification_service: CertificationService = Depends(get_certification_service)
):
    """
    Create multiple certification entries for the current user.
    """
    return await certification_service.create_certifications(
        user_id=current_user.id,
        certifications_data=certifications
    )

@certification_router.get("/", response_model=List[CertificationResponse])
async def get_user_certifications(
    current_user: User = Depends(get_current_user),
    certification_service: CertificationService = Depends(get_certification_service)
):
    """
    Get all certification entries for the current user.
    """
    return await certification_service.get_user_certifications(user_id=current_user.id)

@certification_router.get("/{certification_id}", response_model=CertificationResponse)
async def get_certification(
    certification_id: str,
    current_user: User = Depends(get_current_user),
    certification_service: CertificationService = Depends(get_certification_service)
):
    """
    Get a specific certification entry by ID.
    """
    try:
        obj_id = ObjectId(certification_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid certification ID format"
        )
        
    certification = await certification_service.get_certification(
        user_id=current_user.id,
        certification_id=obj_id
    )
    
    if not certification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignal.CERTIFICATION_NOT_FOUND.value
        )
        
    return certification

@certification_router.put("/{certification_id}", response_model=CertificationResponse)
async def update_certification(
    certification_id: str,
    update_data: CertificationUpdate,
    current_user: User = Depends(get_current_user),
    certification_service: CertificationService = Depends(get_certification_service)
):
    """
    Update a specific certification entry by ID.
    """
    try:
        obj_id = ObjectId(certification_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid certification ID format"
        )
        
    updated_certification = await certification_service.update_certification(
        user_id=current_user.id,
        certification_id=obj_id,
        update_data=update_data
    )
    
    return updated_certification

@certification_router.delete("/{certification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_certification(
    certification_id: str,
    current_user: User = Depends(get_current_user),
    certification_service: CertificationService = Depends(get_certification_service)
):
    """
    Delete a specific certification entry by ID.
    """
    try:
        obj_id = ObjectId(certification_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid certification ID format"
        )
        
    result = await certification_service.delete_certification(
        user_id=current_user.id,
        certification_id=obj_id
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignal.CERTIFICATION_NOT_FOUND.value
        )
