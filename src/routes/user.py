from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from core.config import Settings, get_settings
from dto.user import UserCreate, UserUpdate, UserResponse, UserLogin, UserRegistrationResponse, ResendOTPRequest
from services.user import UserService, get_user_service
from services.otp import OTPService, get_otp_service
from core.security import create_access_token, verify_password
from enums import ResponseSignal 
from schemas.user import User
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
    Only allows login for verified users.
    
    Returns a 401 status code for invalid credentials.
    Returns a 403 status code for unverified users.
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
                    "message": ResponseSignal.INCORRECT_CREDENTIALS.value
                }
            )
        
        # Check if user is verified
        if not user.get("is_verified", False):
            logger.warning(f"Login attempt with unverified email: {user_login_data.email}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "status": "error",
                    "message": ResponseSignal.EMAIL_NOT_VERIFIED.value
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
                "message": ResponseSignal.LOGIN_SUCCESS.value,
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

@auth_router.post("/register", response_model=UserRegistrationResponse, tags=["Authentication"])
async def register_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
    otp_service: OTPService = Depends(get_otp_service)
) -> JSONResponse:
    """
    Register a new user with email verification required.
    Sends an OTP to the user's email for verification.
    
    If user exists but is not verified, allows re-registration and resends OTP.
    If user is already verified, returns an error.
    
    Returns a 409 status code if the email is already registered and verified.
    Returns a 201 status code on successful registration with OTP sent.
    """
    try:
        # Convert DTO to Schema
        user_schema = User(**user_data.dict())
        
        # Create user with verification required
        created_user = await user_service.create_user_with_verification(user_schema)
        
        # Send verification OTP
        try:
            await otp_service.create_and_send_otp(
                email=user_data.email,
                purpose="verification"
            )
            logger.info(f"Verification OTP sent to: {user_data.email}")
        except Exception as otp_error:
            logger.error(f"Failed to send verification OTP: {str(otp_error)}")
            # Don't fail registration if OTP fails, user can request resend
        
        logger.info(f"User registered successfully (pending verification): {user_data.email}")
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "status": "success",
                "message": ResponseSignal.EMAIL_VERIFICATION_REQUIRED.value,
                "email": user_data.email,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "is_verified": False,
                "requires_verification": True
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
                "message": ResponseSignal.REGISTRATION_SERVER_ERROR.value
            }
        )

@auth_router.post("/resend-verification-otp", tags=["Authentication"])
async def resend_verification_otp(
    resend_request: ResendOTPRequest,
    user_service: UserService = Depends(get_user_service),
    otp_service: OTPService = Depends(get_otp_service)
) -> JSONResponse:
    """
    Resend verification OTP to user's email.
    Includes cooldown protection to prevent abuse.
    
    Returns a 404 if user doesn't exist.
    Returns a 400 if user is already verified.
    Returns a 429 if cooldown period hasn't elapsed.
    Returns a 200 on successful OTP resend.
    """
    try:
        # Check if user exists
        user = await user_service.get_user_by_email(resend_request.email)
        if not user:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "status": "error",
                    "message": "User not found"
                }
            )
        
        # Check if user is already verified
        if user.get("is_verified", False):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status": "error",
                    "message": ResponseSignal.USER_ALREADY_VERIFIED.value
                }
            )
        
        # Check cooldown
        can_send = await otp_service.check_otp_cooldown(
            email=resend_request.email,
            purpose=resend_request.purpose,
            cooldown_minutes=2
        )
        
        if not can_send:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "status": "error", 
                    "message": ResponseSignal.OTP_RESEND_COOLDOWN.value
                }
            )
        
        # Send OTP
        await otp_service.create_and_send_otp(
            email=resend_request.email,
            purpose=resend_request.purpose
        )
        
        logger.info(f"Verification OTP resent to: {resend_request.email}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "message": ResponseSignal.OTP_RESEND_SUCCESS.value
            }
        )
        
    except HTTPException as http_exc:
        logger.error(f"HTTP Error in resend_verification_otp: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Error in resend_verification_otp: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "Server error during OTP resend"
            }
        )

# Keep the existing register endpoint for backward compatibility (without verification)
@auth_router.post("/register-direct", response_model=Dict[str, Any], tags=["Authentication"])
async def register_user_direct(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
) -> JSONResponse:
    """
    Register a new user without email verification (for backward compatibility).
    
    Returns a 409 status code if the email or phone number is already registered.
    Returns a 201 status code on successful registration.
    """
    try:
        await user_service.create_user(user_data)
        
        logger.info(f"User registered successfully (direct): {user_data.email}")
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "status": "success",
                "message": ResponseSignal.USER_CREATION_SUCCESS.value
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