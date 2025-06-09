from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime, date
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import get_settings
from enums import DataBaseCollectionNames, ResponseSignal
from .base import BaseService
from schemas.education import Education
from dto.education import EducationCreate, EducationUpdate, EducationResponse
import logging
from dependencies import get_db_client
from fastapi import Depends
from core.utils import convert_dates_for_storage, prepare_education_for_response, prepare_educations_for_response

class EducationService(BaseService):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseCollectionNames.EDUCATIONS.value]
        self.logger = logging.getLogger(__name__)

    async def create_educations(
        self, 
        user_id: ObjectId, 
        educations_data: List[EducationCreate]
    ) -> List[EducationResponse]:
        try:
            # Prepare educations for insertion
            educations_to_insert = []
            for edu_data in educations_data:
                edu_dict = edu_data.model_dump(exclude_unset=True)
                edu_dict = convert_dates_for_storage(edu_dict)
                edu_dict["user_id"] = user_id
                edu_dict["created_at"] = datetime.utcnow()
                educations_to_insert.append(edu_dict)

            # Insert multiple educations
            if educations_to_insert:
                result = await self.collection.insert_many(educations_to_insert)
                
                # Retrieve inserted educations
                created_educations = await self.collection.find(
                    {"_id": {"$in": result.inserted_ids}}
                ).to_list(None)
                
                # Prepare educations for response DTOs
                prepared_educations = prepare_educations_for_response(created_educations)
                print("prepared_educations: from service " + str(prepared_educations))
                return [EducationResponse(**edu) for edu in prepared_educations]
            
            return []

        except Exception as e:
            self.logger.error(f"Error in create_educations: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.EDUCATION_CREATE_ERROR.value
            )

    async def get_user_educations(self, user_id: ObjectId) -> List[EducationResponse]:
        try:
            educations = await self.collection.find(
                {"user_id": user_id}
            ).sort("start_date", -1).to_list(None)
            
            # Prepare educations for response DTOs
            prepared_educations = prepare_educations_for_response(educations)
            
            return [EducationResponse(**edu) for edu in prepared_educations]

        except Exception as e:  
            self.logger.error(f"Error in get_user_educations: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.EDUCATION_RETRIEVE_ERROR.value
            )

    async def get_education(
        self, 
        user_id: ObjectId, 
        education_id: ObjectId
    ) -> Optional[EducationResponse]:
        try:
            education = await self.collection.find_one({
                "_id": education_id,
                "user_id": user_id
            })
            
            if not education:
                raise HTTPException(status_code=404, detail="Education not found")
            
            # Prepare education for response DTO
            prepared_education = prepare_education_for_response(education)
            
            return EducationResponse(**prepared_education)

        except Exception as e:
            self.logger.error(f"Error in get_education: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.EDUCATION_RETRIEVE_ERROR.value
            )

    async def update_education(
        self, 
        user_id: ObjectId,
        education_id: ObjectId, 
        update_data: EducationUpdate
    ) -> EducationResponse:
        try:
            # Check if education exists and belongs to user
            existing_edu = await self.collection.find_one({
                "_id": education_id,
                "user_id": user_id
            })
            
            if not existing_edu:
                raise HTTPException(status_code=404, detail="Education not found")

            # Prepare update data
            update_dict = update_data.model_dump(exclude_unset=True)
            update_dict = convert_dates_for_storage(update_dict)
            update_dict["updated_at"] = datetime.utcnow()
            
            # Update education
            result = await self.collection.update_one(
                {"_id": education_id},
                {"$set": update_dict}
            )
            
            if result.modified_count == 0:
                raise HTTPException(status_code=400, detail="Update failed")

            # Get updated education
            updated_edu = await self.collection.find_one({"_id": education_id})
            
            # Prepare education for response DTO
            prepared_education = prepare_education_for_response(updated_edu)
            
            return EducationResponse(**prepared_education)

        except Exception as e:
            self.logger.error(f"Error in update_education: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.EDUCATION_UPDATE_ERROR.value
            )

    async def delete_education(
        self, 
        user_id: ObjectId, 
        education_id: ObjectId
    ) -> bool:
        try:
            result = await self.collection.delete_one({
                "_id": education_id,
                "user_id": user_id
            })
            
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Education not found")
                
            return True

        except Exception as e:
            self.logger.error(f"Error in delete_education: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.EDUCATION_DELETE_ERROR.value
            )


def get_education_service(db_client: AsyncIOMotorClient = Depends(get_db_client)):
    return EducationService(db_client)
