from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime, date
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import get_settings
from enums import DataBaseCollectionNames, ResponseSignal
from .base import BaseService
from schemas.personal_project import PersonalProject
from dto.personal_project import PersonalProjectCreate, PersonalProjectUpdate, PersonalProjectResponse
import logging
from dependencies import get_db_client
from fastapi import Depends
from core.utils import convert_dates_for_storage_personal_project, prepare_personal_project_for_response, prepare_personal_projects_for_response

class PersonalProjectService(BaseService):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseCollectionNames.PERSONAL_PROJECTS.value]
        self.logger = logging.getLogger(__name__)

    async def create_personal_projects(
        self, 
        user_id: ObjectId, 
        projects_data: List[PersonalProjectCreate]
    ) -> List[PersonalProjectResponse]:
        try:
            # Prepare projects for insertion
            projects_to_insert = []
            for project_data in projects_data:
                project_dict = project_data.model_dump(exclude_unset=True)
                project_dict = convert_dates_for_storage_personal_project(project_dict)
                project_dict["user_id"] = user_id
                project_dict["created_at"] = datetime.utcnow()
                projects_to_insert.append(project_dict)

            # Insert multiple personal projects
            if projects_to_insert:
                result = await self.collection.insert_many(projects_to_insert)
                
                # Retrieve inserted projects
                created_projects = await self.collection.find(
                    {"_id": {"$in": result.inserted_ids}}
                ).to_list(None)
                
                # Prepare projects for response DTOs
                prepared_projects = prepare_personal_projects_for_response(created_projects)
                print("prepared_projects: from service " + str(prepared_projects))
                return [PersonalProjectResponse(**project) for project in prepared_projects]
            
            return []

        except Exception as e:
            self.logger.error(f"Error in create_personal_projects: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.PERSONAL_PROJECT_CREATE_ERROR.value
            )

    async def get_user_personal_projects(self, user_id: ObjectId) -> List[PersonalProjectResponse]:
        try:
            projects = await self.collection.find(
                {"user_id": user_id}
            ).sort("start_date", -1).to_list(None)
            
            # Prepare projects for response DTOs
            prepared_projects = prepare_personal_projects_for_response(projects)
            
            return [PersonalProjectResponse(**project) for project in prepared_projects]

        except Exception as e:  
            self.logger.error(f"Error in get_user_personal_projects: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.PERSONAL_PROJECT_RETRIEVE_ERROR.value
            )

    async def get_personal_project(
        self, 
        user_id: ObjectId, 
        project_id: ObjectId
    ) -> Optional[PersonalProjectResponse]:
        try:
            project = await self.collection.find_one({
                "_id": project_id,
                "user_id": user_id
            })
            
            if not project:
                raise HTTPException(status_code=404, detail="Personal project not found")
            
            # Prepare project for response DTO
            prepared_project = prepare_personal_project_for_response(project)
            
            return PersonalProjectResponse(**prepared_project)

        except Exception as e:
            self.logger.error(f"Error in get_personal_project: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.PERSONAL_PROJECT_RETRIEVE_ERROR.value
            )

    async def update_personal_project(
        self, 
        user_id: ObjectId,
        project_id: ObjectId, 
        update_data: PersonalProjectUpdate
    ) -> PersonalProjectResponse:
        try:
            # Check if project exists and belongs to user
            existing_project = await self.collection.find_one({
                "_id": project_id,
                "user_id": user_id
            })
            
            if not existing_project:
                raise HTTPException(status_code=404, detail="Personal project not found")

            # Prepare update data
            update_dict = update_data.model_dump(exclude_unset=True)
            update_dict = convert_dates_for_storage_personal_project(update_dict)
            update_dict["updated_at"] = datetime.utcnow()
            
            # Update project
            result = await self.collection.update_one(
                {"_id": project_id},
                {"$set": update_dict}
            )
            
            if result.modified_count == 0:
                raise HTTPException(status_code=400, detail="Update failed")

            # Get updated project
            updated_project = await self.collection.find_one({"_id": project_id})
            
            # Prepare project for response DTO
            prepared_project = prepare_personal_project_for_response(updated_project)
            
            return PersonalProjectResponse(**prepared_project)

        except Exception as e:
            self.logger.error(f"Error in update_personal_project: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.PERSONAL_PROJECT_UPDATE_ERROR.value
            )

    async def delete_personal_project(
        self, 
        user_id: ObjectId, 
        project_id: ObjectId
    ) -> bool:
        try:
            result = await self.collection.delete_one({
                "_id": project_id,
                "user_id": user_id
            })
            
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Personal project not found")
                
            return True

        except Exception as e:
            self.logger.error(f"Error in delete_personal_project: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.PERSONAL_PROJECT_DELETE_ERROR.value
            )


def get_personal_project_service(db_client: AsyncIOMotorClient = Depends(get_db_client)):
    return PersonalProjectService(db_client) 