from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from enums import DataBaseCollectionNames, ResponseSignal
from .base import BaseService
from schemas.link import Link
from dto.link import LinkCreate, LinkUpdate, LinkResponse
import logging
from dependencies import get_db_client
from fastapi import Depends
from core.utils import prepare_links_for_response, prepare_link_for_response

class LinkService(BaseService):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseCollectionNames.LINKS.value]
        self.logger = logging.getLogger(__name__)

    async def create_links(
        self, 
        user_id: ObjectId, 
        links_data: List[LinkCreate]
    ) -> List[LinkResponse]:
        try:
            # Prepare links for insertion
            links_to_insert = []
            for link_data in links_data:
                link_dict = link_data.model_dump(exclude_unset=True)
                link_dict["user_id"] = user_id
                link_dict["created_at"] = datetime.utcnow()
                links_to_insert.append(link_dict)

            # Insert multiple links
            if links_to_insert:
                result = await self.collection.insert_many(links_to_insert)
                
                # Retrieve inserted links
                created_links = await self.collection.find(
                    {"_id": {"$in": result.inserted_ids}}
                ).to_list(None)
                
                prepared_links = prepare_links_for_response(created_links)
                return [LinkResponse(**link) for link in prepared_links]
            
            return []

        except Exception as e:
            self.logger.error(f"Error in create_links: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.LINK_CREATE_ERROR.value
            )

    async def get_user_links(self, user_id: ObjectId) -> List[LinkResponse]:
        try:
            links = await self.collection.find(
                {"user_id": user_id}
            ).sort("website_name", 1).to_list(None)
            
            prepared_links = prepare_links_for_response(links)
            return [LinkResponse(**link) for link in prepared_links]

        except Exception as e:
            self.logger.error(f"Error in get_user_links: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.LINK_RETRIEVE_ERROR.value
            )

    async def get_link(
        self, 
        user_id: ObjectId, 
        link_id: ObjectId
    ) -> Optional[LinkResponse]:
        try:
            link = await self.collection.find_one({
                "_id": link_id,
                "user_id": user_id
            })
            
            if not link:
                raise HTTPException(status_code=404, detail="Link not found")
                
            prepared_link = prepare_link_for_response(link)
            return LinkResponse(**prepared_link)

        except Exception as e:
            self.logger.error(f"Error in get_link: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.LINK_RETRIEVE_ERROR.value
            )

    async def update_link(
        self, 
        user_id: ObjectId,
        link_id: ObjectId, 
        update_data: LinkUpdate
    ) -> LinkResponse:
        try:
            # Check if link exists and belongs to user
            existing_link = await self.collection.find_one({
                "_id": link_id,
                "user_id": user_id
            })
            
            if not existing_link:
                raise HTTPException(status_code=404, detail="Link not found")

            # Prepare update data
            update_dict = update_data.model_dump(exclude_unset=True)
            update_dict["updated_at"] = datetime.utcnow()

            # Update link
            result = await self.collection.update_one(
                {"_id": link_id},
                {"$set": update_dict}
            )
            
            if result.modified_count == 0:
                raise HTTPException(status_code=400, detail="Update failed")

            # Get updated link
            updated_link = await self.collection.find_one({"_id": link_id})
            prepared_link = prepare_link_for_response(updated_link)
            return LinkResponse(**prepared_link)

        except Exception as e:
            self.logger.error(f"Error in update_link: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.LINK_UPDATE_ERROR.value
            )

    async def delete_link(
        self, 
        user_id: ObjectId, 
        link_id: ObjectId
    ) -> bool:
        try:
            result = await self.collection.delete_one({
                "_id": link_id,
                "user_id": user_id
            })
            
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Link not found")
                
            return True

        except Exception as e:
            self.logger.error(f"Error in delete_link: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.LINK_DELETE_ERROR.value
            )


def get_link_service(db_client: AsyncIOMotorClient = Depends(get_db_client)):
    return LinkService(db_client)

