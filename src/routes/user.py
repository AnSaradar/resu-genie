from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from typing import List
from core.config import Settings, get_settings
from dto.user import UserCreate, UserUpdate, UserResponse, UserLogin
from services.user import UserService
from core.security import create_access_token, verify_password
from enums import ResponseSignal 
import logging

logger = logging.getLogger(__name__)

auth_router = APIRouter(
    prefix="/api/v1/auth",
    tags=["api_v1", "auth"],
)

# Auth endpoints
@auth_router.post("/login", tags=["Authentication"])
async def login(
    request: Request,
    user_login_data: UserLogin,
    app_settings: Settings = Depends(get_settings)
):
    try:
        user_service = UserService(request.app.db_client)
        user = await user_service.get_user_by_email(user_login_data.email)
        
        if not user or not verify_password(user_login_data.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ResponseSignal.INCORRECT_CREDENTIALS.value
            )
        
        #role = "admin" if user.get("is_admin", False) else "user"
        access_token = create_access_token(
            user_id=str(user["_id"]),
            email=user["email"],
            role="user"
        )
        
        logger.info(ResponseSignal.LOGIN_SUCCESS.value)
        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={
                "access_token": access_token,
                "token_type": "bearer"
            }
        )
    
    
    except HTTPException as http_exc:  # Catch specific HTTP exceptions
        return JSONResponse(
            status_code=http_exc.status_code,
            content={"signal": ResponseSignal.LOGIN_FAILED.value, "detail": http_exc.detail}
        )
    
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"signal": ResponseSignal.LOGIN_FAILED.value})

@auth_router.post("/register", response_model=UserResponse, tags=["Authentication"])
async def register_user(
    request: Request,
    user_data: UserCreate,
):
    try:
        user_service = UserService(request.app.db_client)
        user_data = await user_service.create_user(user_data)
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"signal": ResponseSignal.USER_CREATION_SUCCESS.value}
              # Add user ID to response header for future reference.
        )
    
    except HTTPException as http_exc:  # Catch specific HTTP exceptions
        return JSONResponse(
            status_code=http_exc.status_code,
            content={"signal": ResponseSignal.USER_CREATION_FAILED.value, "detail": http_exc.detail}
        )
    
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"signal": ResponseSignal.USER_CREATION_FAILED.value})

# User management endpoints
# @auth_router.get("/me", response_model=UserResponse, tags=["User"])
# async def get_user_profile(
#     current_user: dict = Depends(get_current_user)
# ):
#     return current_user

# @auth_router.put("/me", response_model=UserResponse, tags=["User"])
# async def update_user_profile(
#     update_data: UserUpdate,
#     current_user: dict = Depends(get_current_user),
#     db: AsyncIOMotorClient = Depends(get_db)
# ):
#     user_service = UserService(db)
#     updated_user = await user_service.update_user(
#         str(current_user["id"]),
#         update_data.dict(exclude_unset=True)
#     )
#     if not updated_user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return updated_user