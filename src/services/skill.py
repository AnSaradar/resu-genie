from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from enums import DataBaseCollectionNames, ResponseSignal
from .base import BaseService
from schemas.skill import Skill
from dto.skill import SkillCreate, SkillUpdate, SkillResponse, SkillsGroupResponse
import logging
from dependencies import get_db_client
from fastapi import Depends
from core.utils import prepare_skill_for_response, prepare_skills_for_response

class SkillService(BaseService):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseCollectionNames.SKILLS.value]
        self.logger = logging.getLogger(__name__)

    
    async def create_skills(
        self, 
        user_id: ObjectId, 
        skills_data: List[SkillCreate]
    ) -> List[SkillResponse]:
        try:
            # Prepare skills for insertion
            skills_to_insert = []
            for skill_data in skills_data:
                skill_dict = skill_data.model_dump(exclude_unset=True)
                skill_dict["user_id"] = user_id
                skill_dict["created_at"] = datetime.utcnow()
                skills_to_insert.append(skill_dict)

            # Insert multiple skills
            if skills_to_insert:
                result = await self.collection.insert_many(skills_to_insert)
                # Retrieve inserted skills
                created_skills = await self.collection.find(
                    {"_id": {"$in": result.inserted_ids}}
                ).to_list(None)
                
                # Prepare skills for response DTOs
                prepared_skills = prepare_skills_for_response(created_skills)
                return [SkillResponse(**skill) for skill in prepared_skills]
            
            return []

        except Exception as e:
            self.logger.error(f"Error in create_skills: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.SKILL_CREATE_ERROR.value
            )

    async def get_user_skills(self, user_id: ObjectId) -> List[SkillResponse]:
        try:
            skills = await self.collection.find(
                {"user_id": user_id}
            ).sort("name", 1).to_list(None)
            
            # Prepare skills for response DTOs
            prepared_skills = prepare_skills_for_response(skills)
            
            return [SkillResponse(**skill) for skill in prepared_skills]

        except Exception as e:
            self.logger.error(f"Error in get_user_skills: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.SKILL_RETRIEVE_ERROR.value
            )

    async def get_skill(
        self, 
        user_id: ObjectId, 
        skill_id: ObjectId
    ) -> Optional[SkillResponse]:
        try:
            skill = await self.collection.find_one({
                "_id": skill_id,
                "user_id": user_id
            })
            
            if not skill:
                raise HTTPException(status_code=404, detail="Skill not found")
            
            # Prepare skill for response DTO
            prepared_skill = prepare_skill_for_response(skill)
                
            return SkillResponse(**prepared_skill)

        except Exception as e:
            self.logger.error(f"Error in get_skill: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.SKILL_RETRIEVE_ERROR.value
            )

    async def update_skill(
        self, 
        user_id: ObjectId,
        skill_id: ObjectId, 
        update_data: SkillUpdate
    ) -> SkillResponse:
        try:
            # Check if skill exists and belongs to user
            existing_skill = await self.collection.find_one({
                "_id": skill_id,
                "user_id": user_id
            })
            
            if not existing_skill:
                raise HTTPException(status_code=404, detail="Skill not found")

            # Prepare update data
            update_dict = update_data.model_dump(exclude_unset=True)
            update_dict["updated_at"] = datetime.utcnow()

            # Update skill
            result = await self.collection.update_one(
                {"_id": skill_id},
                {"$set": update_dict}
            )
            
            if result.modified_count == 0:
                raise HTTPException(status_code=400, detail="Update failed")

            # Get updated skill
            updated_skill = await self.collection.find_one({"_id": skill_id})
            
            # Prepare skill for response DTO
            prepared_skill = prepare_skill_for_response(updated_skill)
            
            return SkillResponse(**prepared_skill)

        except Exception as e:
            self.logger.error(f"Error in update_skill: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.SKILL_UPDATE_ERROR.value
            )

    async def delete_skill(
        self, 
        user_id: ObjectId, 
        skill_id: ObjectId
    ) -> bool:
        try:
            result = await self.collection.delete_one({
                "_id": skill_id,
                "user_id": user_id
            })
            
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Skill not found")
                
            return True

        except Exception as e:
            self.logger.error(f"Error in delete_skill: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.SKILL_DELETE_ERROR.value
            )
    
    async def group_skills_by_proficiency(self, user_id: ObjectId) -> List[SkillsGroupResponse]:
        """
        Group user skills by proficiency level
        """
        try:
            skills = await self.get_user_skills(user_id)
            
            # Group skills by proficiency
            grouped_skills = {}
            
            for skill in skills:
                proficiency = skill.proficiency.value if skill.proficiency else "Unspecified"
                
                if proficiency not in grouped_skills:
                    grouped_skills[proficiency] = []
                    
                grouped_skills[proficiency].append(skill)
            
            # Convert to response format
            result = []
            for category, skills_list in grouped_skills.items():
                result.append(SkillsGroupResponse(
                    category=category,
                    skills=skills_list
                ))
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error in group_skills_by_proficiency: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.SKILL_RETRIEVE_ERROR.value
            )


def get_skill_service(db_client: AsyncIOMotorClient = Depends(get_db_client)):
    return SkillService(db_client)

