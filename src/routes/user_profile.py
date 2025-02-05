from fastapi import APIRouter, Depends, HTTPException, status
import logging
from fastapi.responses import JSONResponse
from enums import ResponseSignal 
from services.user_profile import UserProfileService, get_profile_service
from dto.user_profile import UserProfileCreateUpdate, UserProfileResponse
from core.dependencies import get_current_user
from controllers.BaseController import BaseController

logger = logging.getLogger(__name__)

user_profile_router = APIRouter(
    prefix="/api/v1/user_profile",
    tags=["api_v1", "user_profile"],
)

@user_profile_router.post("/post", response_model=UserProfileResponse)
async def create_or_update_profile(
    profile_data: UserProfileCreateUpdate,
    current_user: dict = Depends(get_current_user),  # Extract user_id from JWT
    profile_service: UserProfileService = Depends(get_profile_service)
):
    """Create or update a user profile (Authenticated user only)"""
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
    profile_service: UserProfileService = Depends(get_profile_service)
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
