from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from enums import DataBaseCollectionNames, ResponseSignal, LanguageProficiency
from .base import BaseService
from schemas.language import Language
from dto.language import LanguageCreate, LanguageUpdate, LanguageResponse, LanguagesGroupResponse
import logging
from dependencies import get_db_client
from fastapi import Depends

class LanguageService(BaseService):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseCollectionNames.LANGUAGES.value]
        self.logger = logging.getLogger(__name__)

    async def create_languages(
        self, 
        user_id: ObjectId, 
        languages_data: List[LanguageCreate]
    ) -> List[LanguageResponse]:
        try:
            # Prepare languages for insertion
            languages_to_insert = []
            for language_data in languages_data:
                language_dict = language_data.model_dump(exclude_unset=True)
                language_dict["user_id"] = user_id
                language_dict["created_at"] = datetime.utcnow()
                languages_to_insert.append(language_dict)

            # Insert multiple languages
            if languages_to_insert:
                result = await self.collection.insert_many(languages_to_insert)
                
                # Retrieve inserted languages
                created_languages = await self.collection.find(
                    {"_id": {"$in": result.inserted_ids}}
                ).to_list(None)
                
                return [LanguageResponse(**language) for language in created_languages]
            
            return []

        except Exception as e:
            self.logger.error(f"Error in create_languages: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.LANGUAGE_CREATE_ERROR.value
            )

    async def get_user_languages(self, user_id: ObjectId) -> List[LanguageResponse]:
        try:
            languages = await self.collection.find(
                {"user_id": user_id}
            ).sort("name", 1).to_list(None)
            
            return [LanguageResponse(**language) for language in languages]

        except Exception as e:
            self.logger.error(f"Error in get_user_languages: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.LANGUAGE_RETRIEVE_ERROR.value
            )

    async def get_language(
        self, 
        user_id: ObjectId, 
        language_id: ObjectId
    ) -> Optional[LanguageResponse]:
        try:
            language = await self.collection.find_one({
                "_id": language_id,
                "user_id": user_id
            })
            
            if not language:
                raise HTTPException(status_code=404, detail="Language not found")
                
            return LanguageResponse(**language)

        except Exception as e:
            self.logger.error(f"Error in get_language: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.LANGUAGE_RETRIEVE_ERROR.value
            )

    async def update_language(
        self, 
        user_id: ObjectId,
        language_id: ObjectId, 
        update_data: LanguageUpdate
    ) -> LanguageResponse:
        try:
            # Check if language exists and belongs to user
            existing_language = await self.collection.find_one({
                "_id": language_id,
                "user_id": user_id
            })
            
            if not existing_language:
                raise HTTPException(status_code=404, detail="Language not found")

            # Prepare update data
            update_dict = update_data.model_dump(exclude_unset=True)
            update_dict["updated_at"] = datetime.utcnow()

            # Update language
            result = await self.collection.update_one(
                {"_id": language_id},
                {"$set": update_dict}
            )
            
            if result.modified_count == 0:
                raise HTTPException(status_code=400, detail="Update failed")

            # Get updated language
            updated_language = await self.collection.find_one({"_id": language_id})
            return LanguageResponse(**updated_language)

        except Exception as e:
            self.logger.error(f"Error in update_language: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.LANGUAGE_UPDATE_ERROR.value
            )

    async def delete_language(
        self, 
        user_id: ObjectId, 
        language_id: ObjectId
    ) -> bool:
        try:
            result = await self.collection.delete_one({
                "_id": language_id,
                "user_id": user_id
            })
            
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Language not found")
                
            return True

        except Exception as e:
            self.logger.error(f"Error in delete_language: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.LANGUAGE_DELETE_ERROR.value
            )
    
    async def group_languages_by_proficiency(self, user_id: ObjectId) -> List[LanguagesGroupResponse]:
        """
        Group user languages by proficiency level
        """
        try:
            languages = await self.get_user_languages(user_id)
            
            # Group languages by proficiency
            grouped_languages = {}
            
            # Define proficiency order for sorting
            proficiency_order = {
                LanguageProficiency.NATIVE.value: 1,
                LanguageProficiency.FLUENT.value: 2,
                LanguageProficiency.ADVANCED.value: 3,
                LanguageProficiency.INTERMEDIATE.value: 4,
                LanguageProficiency.BASIC.value: 5
            }
            
            for language in languages:
                proficiency = language.proficiency.value
                
                if proficiency not in grouped_languages:
                    grouped_languages[proficiency] = []
                    
                grouped_languages[proficiency].append(language)
            
            # Convert to response format and sort by proficiency level
            result = []
            for proficiency, languages_list in grouped_languages.items():
                result.append(LanguagesGroupResponse(
                    proficiency_level=proficiency,
                    languages=sorted(languages_list, key=lambda x: x.name)
                ))
                
            # Sort groups by proficiency level (Native first, then Fluent, etc.)
            result.sort(key=lambda x: proficiency_order.get(x.proficiency_level, 999))
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error in group_languages_by_proficiency: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.LANGUAGE_RETRIEVE_ERROR.value
            )


def get_language_service(db_client: AsyncIOMotorClient = Depends(get_db_client)):
    return LanguageService(db_client)

