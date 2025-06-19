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
from core.utils import prepare_language_for_response, prepare_languages_for_response

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
                # Ensure is_native has a default value
                if "is_native" not in language_dict:
                    language_dict["is_native"] = False
                languages_to_insert.append(language_dict)

            # Insert multiple languages
            if languages_to_insert:
                result = await self.collection.insert_many(languages_to_insert)
                
                # Retrieve inserted languages
                created_languages = await self.collection.find(
                    {"_id": {"$in": result.inserted_ids}}
                ).to_list(None)

                # Prepare languages for response DTOs
                prepared_languages = prepare_languages_for_response(created_languages)
                return [LanguageResponse(**language) for language in prepared_languages]
            
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
            
            # Prepare languages for response DTOs
            prepared_languages = prepare_languages_for_response(languages)
            return [LanguageResponse(**language) for language in prepared_languages]

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
                
            return LanguageResponse(**prepare_language_for_response(language))

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
            return LanguageResponse(**prepare_language_for_response(updated_language))

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
        Group user languages by proficiency level with native languages prioritized
        """
        try:
            languages = await self.get_user_languages(user_id)
            
            # Separate native and non-native languages
            native_languages = [lang for lang in languages if lang.is_native]
            non_native_languages = [lang for lang in languages if not lang.is_native]
            
            # Group non-native languages by proficiency
            grouped_languages = {}
            
            # Define proficiency order for sorting (fixed the enum values)
            proficiency_order = {
                LanguageProficiency.C2.value: 1,
                LanguageProficiency.C1.value: 2,
                LanguageProficiency.B2.value: 3,
                LanguageProficiency.B1.value: 4,
                LanguageProficiency.A2.value: 5,
                LanguageProficiency.A1.value: 6
            }
            
            # Group non-native languages
            for language in non_native_languages:
                proficiency = language.proficiency.value
                
                if proficiency not in grouped_languages:
                    grouped_languages[proficiency] = []
                    
                grouped_languages[proficiency].append(language)
            
            # Convert to response format
            result = []
            
            # Add native languages group first if any
            if native_languages:
                result.append(LanguagesGroupResponse(
                    proficiency_level="Native",
                    languages=sorted(native_languages, key=lambda x: x.name)
                ))
            
            # Add other proficiency groups
            for proficiency, languages_list in grouped_languages.items():
                result.append(LanguagesGroupResponse(
                    proficiency_level=proficiency,
                    languages=sorted(languages_list, key=lambda x: x.name)
                ))
                
            # Sort non-native groups by proficiency level (C2 first, then C1, etc.)
            non_native_groups = [group for group in result if group.proficiency_level != "Native"]
            non_native_groups.sort(key=lambda x: proficiency_order.get(x.proficiency_level, 999))
            
            # Combine: Native first, then sorted proficiency groups
            native_groups = [group for group in result if group.proficiency_level == "Native"]
            result = native_groups + non_native_groups
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error in group_languages_by_proficiency: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=ResponseSignal.LANGUAGE_RETRIEVE_ERROR.value
            )


def get_language_service(db_client: AsyncIOMotorClient = Depends(get_db_client)):
    return LanguageService(db_client)

