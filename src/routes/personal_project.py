from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from bson import ObjectId
from services.personal_project import PersonalProjectService, get_personal_project_service
from dto.personal_project import PersonalProjectCreate, PersonalProjectUpdate, PersonalProjectResponse
from dependencies import get_current_user
from schemas.user import User
from enums import ResponseSignal
from controllers.BaseController import BaseController
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

personal_project_router = APIRouter(
    prefix="/api/v1/personal-project",
    tags=["api_v1","personal_project"],
)

@personal_project_router.post("/", response_model=List[PersonalProjectResponse], status_code=status.HTTP_201_CREATED)
async def create_personal_projects(
    projects: List[PersonalProjectCreate],
    current_user: User = Depends(get_current_user),
    personal_project_service: PersonalProjectService = Depends(get_personal_project_service)
):
    """
    Create multiple personal project entries for the current user.
    """
    user_id = current_user["_id"] 
    try:
        created_projects = await personal_project_service.create_personal_projects(
            user_id=user_id,
            projects_data=projects
        )
        
        projects_data = BaseController().get_json_serializable_object(created_projects)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "signal": ResponseSignal.PERSONAL_PROJECT_CREATE_SUCCESS.value,
                "personal_projects": projects_data
            }
        )   
    except Exception as e:
        logger.error(f"Error adding personal projects: {str(e)}")
        raise HTTPException(
            status_code=400, 
            detail=ResponseSignal.PERSONAL_PROJECT_CREATE_ERROR.value
        )


@personal_project_router.get("/", response_model=List[PersonalProjectResponse])
async def get_user_personal_projects(
    current_user: User = Depends(get_current_user),
    personal_project_service: PersonalProjectService = Depends(get_personal_project_service)
):
    """
    Get all personal project entries for the current user.
    """
    user_id = current_user["_id"]
    try:
        user_projects = await personal_project_service.get_user_personal_projects(user_id=user_id)

        projects_data = BaseController().get_json_serializable_object(user_projects)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.PERSONAL_PROJECT_RETRIEVE_SUCCESS.value,
                "personal_projects": projects_data
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=ResponseSignal.PERSONAL_PROJECT_RETRIEVE_ERROR.value
        )


@personal_project_router.get("/{project_id}", response_model=PersonalProjectResponse)
async def get_personal_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    personal_project_service: PersonalProjectService = Depends(get_personal_project_service)
):
    """
    Get a specific personal project entry by ID.
    """
    user_id = current_user["_id"]
    try:
        obj_id = ObjectId(project_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid personal project ID format"
        )
        
    project = await personal_project_service.get_personal_project(
        user_id=user_id,
        project_id=obj_id
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignal.PERSONAL_PROJECT_NOT_FOUND.value
        )
        
    project_data = BaseController().get_json_serializable_object(project)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.PERSONAL_PROJECT_RETRIEVE_SUCCESS.value,
            "personal_project": project_data
        }
    )


@personal_project_router.put("/{project_id}", response_model=PersonalProjectResponse)
async def update_personal_project(
    project_id: str,
    update_data: PersonalProjectUpdate,
    current_user: User = Depends(get_current_user),
    personal_project_service: PersonalProjectService = Depends(get_personal_project_service)
):
    """
    Update a specific personal project entry by ID.
    """
    user_id = current_user["_id"]
    try:
        obj_id = ObjectId(project_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid personal project ID format"
        )
        
    updated_project = await personal_project_service.update_personal_project(
        user_id=user_id,
        project_id=obj_id,
        update_data=update_data
    )
    
    project_data = BaseController().get_json_serializable_object(updated_project)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.PERSONAL_PROJECT_UPDATE_SUCCESS.value,
            "personal_project": project_data
        }
    )


@personal_project_router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_personal_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    personal_project_service: PersonalProjectService = Depends(get_personal_project_service)
):
    """
    Delete a specific personal project entry by ID.
    """
    user_id = current_user["_id"]
    try:
        obj_id = ObjectId(project_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid personal project ID format"
        )
        
    result = await personal_project_service.delete_personal_project(
        user_id=user_id,
        project_id=obj_id
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseSignal.PERSONAL_PROJECT_NOT_FOUND.value
        )
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content={
            "signal": ResponseSignal.PERSONAL_PROJECT_DELETE_SUCCESS.value
        }
    ) 