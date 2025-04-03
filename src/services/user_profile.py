from typing import Optional
from bson import ObjectId
from fastapi import HTTPException, Depends
from datetime import datetime
from enums import DataBaseCollectionNames, WorkField
from .base import BaseService
from schemas.user_profile import UserProfile
from dto.user_profile import UserProfileResponse
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import get_settings
from enums import ResponseSignal
from dependencies import get_db_client

class UserProfileService(BaseService):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseCollectionNames.USERS_PROFILES.value]
        self.logger = logging.getLogger(__name__)

    async def create_or_update_user_profile(
        self, 
        user_id: ObjectId, 
        profile_data: UserProfile
    ) -> UserProfile:
        try:
            # Check if profile exists
            existing_profile = await self.collection.find_one({"user_id": user_id})
            
            # Prepare profile data
            profile_dict = profile_data.model_dump(exclude={"id"}, exclude_unset=True)
            profile_dict["user_id"] = user_id
            profile_dict["birth_date"] = datetime.combine(profile_data.birth_date, datetime.min.time())
            
            # Convert WorkField enum to string if it exists
            if profile_dict.get("work_field") and isinstance(profile_dict["work_field"], WorkField):
                profile_dict["work_field"] = profile_dict["work_field"].value

            if existing_profile:
                # Update existing profile
                self.logger.info("Profile exists, updating...")
                profile_dict["updated_at"] = datetime.utcnow()
                result = await self.collection.update_one(
                    {"user_id": user_id},
                    {"$set": profile_dict}
                )
                if result.modified_count == 0:
                    raise HTTPException(
                        status_code=400,
                        detail="Profile update failed"
                    )
            else:
                # Create new profile
                self.logger.info("Profile does not exist, creating...")
                profile_dict["created_at"] = datetime.utcnow()
                result = await self.collection.insert_one(profile_dict)

            # Get updated/created profile
            updated_profile = await self.collection.find_one({"user_id": user_id})
            self.logger.info(f"Profile created/updated successfully")
            return await self._convert_to_response(updated_profile)

        except Exception as e:
            self.logger.error(f"Error in create_or_update_user_profile: {str(e)}")
            raise HTTPException(status_code=400, detail=ResponseSignal.USER_PROFILE_ERROR.value)

    async def get_user_profile(self, user_id: ObjectId) -> Optional[UserProfile]:
        try:
            profile = await self.collection.find_one({"user_id": user_id})
            if not profile:
                raise HTTPException(
                    status_code=404,
                    detail="Profile not found"
                )
            
            return await self._convert_to_response(profile)
            
        except Exception as e:
            self.logger.error(f"Error in get_user_profile: {str(e)}")
            raise HTTPException(status_code=400, detail=ResponseSignal.USER_PROFILE_RETRIVE_ERROR.value)

    async def update_user_profile(
        self, 
        user_id: ObjectId, 
        update_data: UserProfile
    ) -> UserProfile:
        try:
            # Check if profile exists
            existing_profile = await self.collection.find_one({"user_id": user_id})
            if not existing_profile:
                raise HTTPException(
                    status_code=404,
                    detail="Profile not found"
                )

            # Prepare update data
            update_dict = update_data.model_dump(
                exclude={"id", "user_id", "created_at"}, 
                exclude_unset=True
            )
            
            # Convert WorkField enum to string if it exists
            if update_dict.get("work_field") and isinstance(update_dict["work_field"], WorkField):
                update_dict["work_field"] = update_dict["work_field"].value
                
            update_dict["updated_at"] = datetime.utcnow()

            # Update profile
            result = await self.collection.update_one(
                {"user_id": user_id},
                {"$set": update_dict}
            )
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Profile update failed"
                )

            # Get updated profile
            updated_profile = await self.collection.find_one({"user_id": user_id})
            return await self._convert_to_response(updated_profile)

        except Exception as e:
            self.logger.error(f"Error in update_user_profile: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def delete_user_profile(self, user_id: ObjectId) -> bool:
        """This method should only be called when deleting a user"""
        try:
            result = await self.collection.delete_one({"user_id": user_id})
            if result.deleted_count == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Profile not found"
                )
            return True
        except Exception as e:
            self.logger.error(f"Error in delete_user_profile: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
            
    async def _convert_to_response(self, profile: dict) -> UserProfileResponse:
        """Convert a MongoDB profile to a UserProfileResponse"""
        # Convert datetime to date for birth_date
        if "birth_date" in profile and isinstance(profile["birth_date"], datetime):
            profile["birth_date"] = profile["birth_date"].date()
            
        # Convert work_field string to enum if it exists
        if "work_field" in profile and profile["work_field"] is not None:
            try:
                profile["work_field"] = WorkField(profile["work_field"])
            except ValueError:
                # If the value doesn't match any enum, set to None or OTHER
                profile["work_field"] = WorkField.OTHER
        
        return UserProfileResponse(**profile)

def get_user_profile_service(db_client: AsyncIOMotorClient = Depends(get_db_client)):
    return UserProfileService(db_client)
