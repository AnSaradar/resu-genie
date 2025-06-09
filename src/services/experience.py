from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime, date
from motor.motor_asyncio import AsyncIOMotorClient
from enums import DataBaseCollectionNames, ResponseSignal
from .base import BaseService
from schemas.experiance import Experience
from dto.experiance import ExperienceCreate, ExperienceUpdate, ExperienceResponse
import logging
from dependencies import get_db_client
from fastapi import Depends
from core.utils import convert_dates_for_storage, prepare_experience_for_response, prepare_experiences_for_response

class ExperienceService(BaseService):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseCollectionNames.EXPERIENCES.value]
        self.logger = logging.getLogger(__name__)

    async def create_experiences(
        self, 
        user_id: ObjectId, 
        experiences_data: List[ExperienceCreate]
    ) -> List[ExperienceResponse]:
        try:
            # Prepare experiences for insertion
            experiences_to_insert = []
            for exp_data in experiences_data:
                exp_dict = exp_data.model_dump(exclude_unset=True)
                
                # Convert date objects to datetime objects for MongoDB compatibility
                exp_dict = convert_dates_for_storage(exp_dict)
                
                exp_dict["user_id"] = user_id
                exp_dict["created_at"] = datetime.utcnow()
                experiences_to_insert.append(exp_dict)

            # Insert multiple experiences
            if experiences_to_insert:
                result = await self.collection.insert_many(experiences_to_insert)
                
                # Retrieve inserted experiences
                created_experiences = await self.collection.find(
                    {"_id": {"$in": result.inserted_ids}}
                ).to_list(None)
                
                # Prepare experiences for response DTOs
                prepared_experiences = prepare_experiences_for_response(created_experiences)
                
                return [ExperienceResponse(**exp) for exp in prepared_experiences]
            
            return []

        except Exception as e:
            self.logger.error(f"Error in create_experiences: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.EXPERIENCE_CREATE_ERROR.value
            )

    async def get_user_experiences(self, user_id: ObjectId) -> List[ExperienceResponse]:
        try:
            experiences = await self.collection.find(
                {"user_id": user_id}
            ).sort("start_date", -1).to_list(None)
            
            # Prepare experiences for response DTOs
            prepared_experiences = prepare_experiences_for_response(experiences)
            
            return [ExperienceResponse(**exp) for exp in prepared_experiences]

        except Exception as e:
            self.logger.error(f"Error in get_user_experiences: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.EXPERIENCE_RETRIEVE_ERROR.value
            )

    async def get_experience(
        self, 
        user_id: ObjectId, 
        experience_id: ObjectId
    ) -> Optional[ExperienceResponse]:
        try:
            experience = await self.collection.find_one({
                "_id": experience_id,
                "user_id": user_id
            })
            
            if not experience:
                raise HTTPException(status_code=404, detail="Experience not found")
            
            # Prepare experience for response DTO
            prepared_experience = prepare_experience_for_response(experience)
                
            return ExperienceResponse(**prepared_experience)

        except Exception as e:
            self.logger.error(f"Error in get_experience: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.EXPERIENCE_RETRIEVE_ERROR.value
            )

    async def update_experience(
        self, 
        user_id: ObjectId,
        experience_id: ObjectId, 
        update_data: ExperienceUpdate
    ) -> ExperienceResponse:
        try:
            # Check if experience exists and belongs to user
            existing_exp = await self.collection.find_one({
                "_id": experience_id,
                "user_id": user_id
            })
            
            if not existing_exp:
                raise HTTPException(status_code=404, detail="Experience not found")

            # Prepare update data
            update_dict = update_data.model_dump(exclude_unset=True)
            
            # Convert date objects to datetime objects for MongoDB compatibility
            update_dict = convert_dates_for_storage(update_dict)
            
            update_dict["updated_at"] = datetime.utcnow()

            # Update experience
            result = await self.collection.update_one(
                {"_id": experience_id},
                {"$set": update_dict}
            )
            
            if result.modified_count == 0:
                raise HTTPException(status_code=400, detail="Update failed")

            # Get updated experience
            updated_exp = await self.collection.find_one({"_id": experience_id})
            
            # Prepare experience for response DTO
            prepared_experience = prepare_experience_for_response(updated_exp)
                
            return ExperienceResponse(**prepared_experience)

        except Exception as e:
            self.logger.error(f"Error in update_experience: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.EXPERIENCE_UPDATE_ERROR.value
            )

    async def delete_experience(
        self, 
        user_id: ObjectId, 
        experience_id: ObjectId
    ) -> bool:
        try:
            result = await self.collection.delete_one({
                "_id": experience_id,
                "user_id": user_id
            })
            
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Experience not found")
                
            return True

        except Exception as e:
            self.logger.error(f"Error in delete_experience: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.EXPERIENCE_DELETE_ERROR.value
            )


def get_experience_service(db_client: AsyncIOMotorClient = Depends(get_db_client)):
    return ExperienceService(db_client)
