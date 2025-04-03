from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from core.config import Settings, get_settings
from dto.user import UserCreate, UserUpdate, UserResponse, UserLogin
from services.user import UserService, get_user_service
from core.security import create_access_token, verify_password
from enums import ResponseSignal 
import logging
from dependencies.auth import get_current_user


logger = logging.getLogger(__name__)

auth_router = APIRouter(
    prefix="/api/v1/auth",
    tags=["api_v1", "auth"],
)

# Auth endpoints
@auth_router.post("/login", tags=["Authentication"])
async def login(
    user_login_data: UserLogin,
    user_service: UserService = Depends(get_user_service)
) -> JSONResponse:
    """
    Authenticate a user and return an access token.
    
    Returns a 401 status code for invalid credentials.
    Returns a 200 status code with an access token on successful login.
    """
    try:
        # Try to find user by email
        user = await user_service.get_user_by_email(user_login_data.email)
        
        # Check if user exists and password is correct
        if not user or not verify_password(user_login_data.password, user["password"]):
            logger.warning(f"Failed login attempt for email: {user_login_data.email}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "status": "error",
                    "message": "Invalid email or password"
                }
            )
        
        # Generate access token with user information
        access_token = create_access_token(
            user_id=str(user["_id"]),
            email=user["email"],
            role="user"
        )
        
        logger.info(f"Successful login for user: {user_login_data.email}")
        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={
                "status": "success",
                "message": "Login successful",
                "access_token": access_token,
                "token_type": "bearer"
            }
        )
    
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "Server error during login"
            }
        )

@auth_router.post("/register", response_model=Dict[str, Any], tags=["Authentication"])
async def register_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
) -> JSONResponse:
    """
    Register a new user.
    
    Returns a 409 status code if the email or phone number is already registered.
    Returns a 201 status code on successful registration.
    """
    try:
        await user_service.create_user(user_data)
        
        logger.info(f"User registered successfully: {user_data.email}")
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "status": "success",
                "message": "User registered successfully"
            }
        )
    
    except HTTPException as http_exc:
        # Handle specific HTTP exceptions from the service
        logger.warning(f"Registration error: {http_exc.detail}")
        return JSONResponse(
            status_code=http_exc.status_code,
            content={
                "status": "error",
                "message": http_exc.detail
            }
        )
    
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "Server error during registration"
            }
        )

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