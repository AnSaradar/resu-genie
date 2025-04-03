from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from enums import DataBaseCollectionNames, ResponseSignal
from .base import BaseService
from schemas.certification import Certification
from dto.certification import CertificationCreate, CertificationUpdate, CertificationResponse
import logging
from dependencies import get_db_client
from fastapi import Depends


class CertificationService(BaseService):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseCollectionNames.CERTIFICATIONS.value]
        self.logger = logging.getLogger(__name__)

    async def create_certifications(
        self, 
        user_id: ObjectId, 
        certifications_data: List[CertificationCreate]
    ) -> List[CertificationResponse]:
        try:
            # Prepare certifications for insertion
            certifications_to_insert = []
            for cert_data in certifications_data:
                cert_dict = cert_data.model_dump(exclude_unset=True)
                cert_dict["user_id"] = user_id
                cert_dict["created_at"] = datetime.utcnow()
                certifications_to_insert.append(cert_dict)

            # Insert multiple certifications
            if certifications_to_insert:
                result = await self.collection.insert_many(certifications_to_insert)
                
                # Retrieve inserted certifications
                created_certifications = await self.collection.find(
                    {"_id": {"$in": result.inserted_ids}}
                ).to_list(None)
                
                return [CertificationResponse(**cert) for cert in created_certifications]
            
            return []

        except Exception as e:
            self.logger.error(f"Error in create_certifications: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.CERTIFICATION_CREATE_ERROR.value
            )

    async def get_user_certifications(self, user_id: ObjectId) -> List[CertificationResponse]:
        try:
            certifications = await self.collection.find(
                {"user_id": user_id}
            ).sort("issue_date", -1).to_list(None)
            
            return [CertificationResponse(**cert) for cert in certifications]

        except Exception as e:
            self.logger.error(f"Error in get_user_certifications: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.CERTIFICATION_RETRIEVE_ERROR.value
            )

    async def get_certification(
        self, 
        user_id: ObjectId, 
        certification_id: ObjectId
    ) -> Optional[CertificationResponse]:
        try:
            certification = await self.collection.find_one({
                "_id": certification_id,
                "user_id": user_id
            })
            
            if not certification:
                raise HTTPException(status_code=404, detail="Certification not found")
                
            return CertificationResponse(**certification)

        except Exception as e:
            self.logger.error(f"Error in get_certification: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.CERTIFICATION_RETRIEVE_ERROR.value
            )

    async def update_certification(
        self, 
        user_id: ObjectId,
        certification_id: ObjectId, 
        update_data: CertificationUpdate
    ) -> CertificationResponse:
        try:
            # Check if certification exists and belongs to user
            existing_cert = await self.collection.find_one({
                "_id": certification_id,
                "user_id": user_id
            })
            
            if not existing_cert:
                raise HTTPException(status_code=404, detail="Certification not found")

            # Prepare update data
            update_dict = update_data.model_dump(exclude_unset=True)
            update_dict["updated_at"] = datetime.utcnow()

            # Update certification
            result = await self.collection.update_one(
                {"_id": certification_id},
                {"$set": update_dict}
            )
            
            if result.modified_count == 0:
                raise HTTPException(status_code=400, detail="Update failed")

            # Get updated certification
            updated_cert = await self.collection.find_one({"_id": certification_id})
            return CertificationResponse(**updated_cert)

        except Exception as e:
            self.logger.error(f"Error in update_certification: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.CERTIFICATION_UPDATE_ERROR.value
            )

    async def delete_certification(
        self, 
        user_id: ObjectId, 
        certification_id: ObjectId
    ) -> bool:
        try:
            result = await self.collection.delete_one({
                "_id": certification_id,
                "user_id": user_id
            })
            
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Certification not found")
                
            return True

        except Exception as e:
            self.logger.error(f"Error in delete_certification: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.CERTIFICATION_DELETE_ERROR.value
            )


def get_certification_service(db_client: AsyncIOMotorClient = Depends(get_db_client)):
    return CertificationService(db_client)

