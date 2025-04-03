from fastapi import APIRouter, Depends, HTTPException, status
import logging
from fastapi.responses import JSONResponse
from enums import ResponseSignal, WorkField
from services.user_profile import UserProfileService, get_user_profile_service
from dto.user_profile import UserProfileCreateUpdate, UserProfileResponse
from dependencies.auth import get_current_user
from controllers.BaseController import BaseController
from typing import List

logger = logging.getLogger(__name__)

user_profile_router = APIRouter(
    prefix="/api/v1/user_profile",
    tags=["api_v1", "user_profile"],
)

@user_profile_router.post("/post", response_model=UserProfileResponse)
async def create_or_update_profile(
    profile_data: UserProfileCreateUpdate,
    current_user: dict = Depends(get_current_user),  # Extract user_id from JWT
    profile_service: UserProfileService = Depends(get_user_profile_service)
):
    """
    Create or update a user profile (Authenticated user only)
    
    Fields include:
    - linkedin_url: Optional LinkedIn profile URL
    - website_url: Optional personal website URL
    - birth_date: Date of birth
    - profile_summary: Optional summary/bio
    - address: Optional physical address
    - current_position: Optional current job title
    - work_field: Optional primary field of work
    - years_of_experience: Optional years of professional experience
    """
    user_id = current_user["user_id"]  # Extract user_id from token

    try:
        updated_profile_data = await profile_service.create_or_update_user_profile(
            user_id, 
            profile_data
        )
        #logger.info(updated_profile_data)
        updated_profile_data = BaseController().get_json_serializable_object(updated_profile_data)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"signal": ResponseSignal.USER_PROFILE_SUCCESS.value, "profile_data": updated_profile_data}
        )
    
    except HTTPException as http_exc:  # Catch specific HTTP exceptions
        return JSONResponse(
            status_code=http_exc.status_code,
            content={"detail": http_exc.detail}
        )
    except Exception as e:
        logger.error(f"Error creating/updating profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseSignal.USER_PROFILE_ERROR.value
        )

@user_profile_router.get("/get", response_model=UserProfileResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user),  # Extract user_id from JWT
    profile_service: UserProfileService = Depends(get_user_profile_service)
):
    """Get the profile of the authenticated user"""
    user_id = current_user["user_id"]  # Extract user_id from token

    try:
        return await profile_service.get_user_profile(user_id)
    except Exception as e:
        logger.error(f"Error retrieving profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

@user_profile_router.get("/work-fields", response_model=List[str])
async def get_work_fields():
    """
    Get a list of all available work fields
    """
    return [field.value for field in WorkField]
