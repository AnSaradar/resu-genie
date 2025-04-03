from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from bson import ObjectId
from services.language import LanguageService, get_language_service
from dto.language import LanguageCreate, LanguageUpdate, LanguageResponse, LanguagesGroupResponse
from dependencies.auth import get_current_user
from schemas.user import User
from enums import ResponseSignal

language_router = APIRouter(
    prefix="/languages",
    tags=["languages"],
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
    return await language_service.create_languages(
        user_id=current_user.id,
        languages_data=languages
    )

@language_router.get("/", response_model=List[LanguageResponse])
async def get_user_languages(
    current_user: User = Depends(get_current_user),
    language_service: LanguageService = Depends(get_language_service)
):
    """
    Get all language entries for the current user.
    """
    return await language_service.get_user_languages(user_id=current_user.id)

@language_router.get("/grouped", response_model=List[LanguagesGroupResponse])
async def get_grouped_languages(
    current_user: User = Depends(get_current_user),
    language_service: LanguageService = Depends(get_language_service)
):
    """
    Get all languages for the current user, grouped by proficiency level.
    """
    return await language_service.group_languages_by_proficiency(user_id=current_user.id)

@language_router.get("/{language_id}", response_model=LanguageResponse)
async def get_language(
    language_id: str,
    current_user: User = Depends(get_current_user),
    language_service: LanguageService = Depends(get_language_service)
):
    """
    Get a specific language entry by ID.
    """
    try:
        obj_id = ObjectId(language_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid language ID format"
        )
        
    language = await language_service.get_language(
        user_id=current_user.id,
        language_id=obj_id
    )
    
    if not language:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignal.LANGUAGE_NOT_FOUND.value
        )
        
    return language

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
    try:
        obj_id = ObjectId(language_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid language ID format"
        )
        
    updated_language = await language_service.update_language(
        user_id=current_user.id,
        language_id=obj_id,
        update_data=update_data
    )
    
    return updated_language

@language_router.delete("/{language_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_language(
    language_id: str,
    current_user: User = Depends(get_current_user),
    language_service: LanguageService = Depends(get_language_service)
):
    """
    Delete a specific language entry by ID.
    """
    try:
        obj_id = ObjectId(language_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid language ID format"
        )
        
    result = await language_service.delete_language(
        user_id=current_user.id,
        language_id=obj_id
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignal.LANGUAGE_NOT_FOUND.value
        ) 