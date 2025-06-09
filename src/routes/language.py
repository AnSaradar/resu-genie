from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from bson import ObjectId
from services.language import LanguageService, get_language_service
from dto.language import LanguageCreate, LanguageUpdate, LanguageResponse, LanguagesGroupResponse
from dependencies.auth import get_current_user
from schemas.user import User
from enums import ResponseSignal
from fastapi.responses import JSONResponse
from controllers.BaseController import BaseController
import logging

logger = logging.getLogger(__name__)

language_router = APIRouter(
    prefix="/api/v1/language",
    tags=["api_v1", "language"],
    responses={404: {"description": "Not found"}},
)

@language_router.post("/", response_model=List[LanguageResponse], status_code=status.HTTP_201_CREATED)
async def create_languages(
    languages: List[LanguageCreate],
    current_user: User = Depends(get_current_user),
    language_service: LanguageService = Depends(get_language_service)
):
    """
    Create multiple language entries for the current user.
    """
    user_id = current_user["_id"]
    try:
        created_languages = await language_service.create_languages(
            user_id=user_id,
            languages_data=languages
        )
        languages_data = BaseController().get_json_serializable_object(created_languages)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "signal": ResponseSignal.LANGUAGE_CREATE_SUCCESS.value,
                "languages": languages_data
            }
        )
    except Exception as e:
        logger.error(f"Error in create_languages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseSignal.LANGUAGE_CREATE_ERROR.value
        )


@language_router.get("/", response_model=List[LanguageResponse])
async def get_user_languages(
    current_user: User = Depends(get_current_user),
    language_service: LanguageService = Depends(get_language_service)
):
    """
    Get all language entries for the current user.
    """
    user_id = current_user["_id"]
    try:
        user_languages = await language_service.get_user_languages(user_id=user_id)
        languages_data = BaseController().get_json_serializable_object(user_languages)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.LANGUAGE_RETRIEVE_SUCCESS.value,
                "languages": languages_data
            }
        )
    except Exception as e:
        logger.error(f"Error in get_user_languages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseSignal.LANGUAGE_RETRIEVE_ERROR.value
        )

@language_router.get("/grouped", response_model=List[LanguagesGroupResponse])
async def get_grouped_languages(
    current_user: User = Depends(get_current_user),
    language_service: LanguageService = Depends(get_language_service)
):
    """
    Get all languages for the current user, grouped by proficiency level.
    """
    user_id = current_user["_id"]
    try:
        user_languages = await language_service.group_languages_by_proficiency(user_id=user_id)
        languages_data = BaseController().get_json_serializable_object(user_languages)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.LANGUAGE_RETRIEVE_SUCCESS.value,
                "languages": languages_data
            }
        )
    except Exception as e:
        logger.error(f"Error in get_grouped_languages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseSignal.LANGUAGE_RETRIEVE_ERROR.value
        )

@language_router.get("/{language_id}", response_model=LanguageResponse)
async def get_language(
    language_id: str,
    current_user: User = Depends(get_current_user),
    language_service: LanguageService = Depends(get_language_service)
):
    """
    Get a specific language entry by ID.
    """
    user_id = current_user["_id"]
    try:
        obj_id = ObjectId(language_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid language ID format"
        )
        
    language = await language_service.get_language(
        user_id=user_id,
        language_id=obj_id
    )
    
    if not language:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignal.LANGUAGE_NOT_FOUND.value,
                "language": None
            }
        )
    language_data = BaseController().get_json_serializable_object(language)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.LANGUAGE_RETRIEVE_SUCCESS.value,
            "language": language_data
        }
    )

@language_router.put("/{language_id}", response_model=LanguageResponse)
async def update_language(
    language_id: str,
    update_data: LanguageUpdate,
    current_user: User = Depends(get_current_user),
    language_service: LanguageService = Depends(get_language_service)
):
    """
    Update a specific language entry by ID.
    """
    user_id = current_user["_id"]
    try:
        obj_id = ObjectId(language_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid language ID format"
        )
        
    updated_language = await language_service.update_language(
        user_id=user_id,
        language_id=obj_id,
        update_data=update_data
    )
    if not updated_language:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignal.LANGUAGE_NOT_FOUND.value,
                "language": None
            }
        )
    language_data = BaseController().get_json_serializable_object(updated_language)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.LANGUAGE_UPDATE_SUCCESS.value,
            "language": language_data
        }
    )

@language_router.delete("/{language_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_language(
    language_id: str,
    current_user: User = Depends(get_current_user),
    language_service: LanguageService = Depends(get_language_service)
):
    """
    Delete a specific language entry by ID.
    """
    user_id = current_user["_id"]
    try:
        obj_id = ObjectId(language_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid language ID format"
        )
        
    result = await language_service.delete_language(
        user_id=user_id,
        language_id=obj_id
    )
    
    if not result:
            return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignal.LANGUAGE_NOT_FOUND.value,
                "language": None
            }
        )
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content={
            "signal": ResponseSignal.LANGUAGE_DELETE_SUCCESS.value,
            "language": None
        }
    )
