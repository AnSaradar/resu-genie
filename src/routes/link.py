from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from bson import ObjectId
from services.link import LinkService, get_link_service
from dto.link import LinkCreate, LinkUpdate, LinkResponse
from dependencies.auth import get_current_user
from schemas.user import User
from enums import ResponseSignal
import logging
from fastapi.responses import JSONResponse
from controllers.BaseController import BaseController

logger = logging.getLogger(__name__)

link_router = APIRouter(
    prefix="/api/v1/link",
    tags=["Link" , "api_v1"],
    responses={404: {"description": "Not found"}},
)

@link_router.post("/", response_model=List[LinkResponse], status_code=status.HTTP_201_CREATED)
async def create_links(
    links: List[LinkCreate],
    current_user: User = Depends(get_current_user),
    link_service: LinkService = Depends(get_link_service)
):
    """
    Create multiple link entries for the current user.
    """
    user_id = current_user["_id"]
    try:
        created_links = await link_service.create_links(
        user_id=user_id,
        links_data=links
    )
        prepared_links = BaseController().get_json_serializable_object(created_links)
        return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "signal": ResponseSignal.LINK_CREATE_SUCCESS.value,
            "links": prepared_links
        }
    )

    except Exception as e:
        logger.error(f"Error in create_links: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseSignal.LINK_CREATE_ERROR.value
        )

@link_router.get("/", response_model=List[LinkResponse])
async def get_user_links(
    current_user: User = Depends(get_current_user),
    link_service: LinkService = Depends(get_link_service)
):
    """
    Get all link entries for the current user.
    """
    user_id = current_user["_id"]
    try:
        links = await link_service.get_user_links(user_id=user_id)
        prepared_links = BaseController().get_json_serializable_object(links)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.LINK_RETRIEVE_SUCCESS.value,
                "links": prepared_links
            }
        )
    except Exception as e:
        logger.error(f"Error in get_user_links: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseSignal.LINK_RETRIEVE_ERROR.value
        )

@link_router.get("/{link_id}", response_model=LinkResponse)
async def get_link(
    link_id: str,
    current_user: User = Depends(get_current_user),
    link_service: LinkService = Depends(get_link_service)
):
    """
    Get a specific link entry by ID.
    """
    user_id = current_user["_id"]
    try:
        obj_id = ObjectId(link_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid link ID format"
        )
        
    link = await link_service.get_link(
        user_id=user_id,
        link_id=obj_id
    )
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignal.LINK_NOT_FOUND.value
        )
        
    prepared_link = BaseController().get_json_serializable_object(link)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.LINK_RETRIEVE_SUCCESS.value,
            "link": prepared_link
        }
    )

@link_router.put("/{link_id}", response_model=LinkResponse)
async def update_link(
    link_id: str,
    update_data: LinkUpdate,
    current_user: User = Depends(get_current_user),
    link_service: LinkService = Depends(get_link_service)
):
    """
    Update a specific link entry by ID.
    """
    user_id = current_user["_id"]
    try:
        obj_id = ObjectId(link_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid link ID format"
        )
        
    updated_link = await link_service.update_link(
        user_id=user_id,
        link_id=obj_id,
        update_data=update_data
    )
    
    prepared_link = BaseController().get_json_serializable_object(updated_link)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.LINK_UPDATE_SUCCESS.value,
            "link": prepared_link
        }
    )

@link_router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    link_id: str,
    current_user: User = Depends(get_current_user),
    link_service: LinkService = Depends(get_link_service)
):
    """
    Delete a specific link entry by ID.
    """
    user_id = current_user["_id"]
    try:
        obj_id = ObjectId(link_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid link ID format"
        )
        
    result = await link_service.delete_link(
        user_id=user_id,
        link_id=obj_id
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignal.LINK_NOT_FOUND.value
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.LINK_DELETE_SUCCESS.value,
        }
    )
