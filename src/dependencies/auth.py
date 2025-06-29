from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional
from dependencies.database import get_db_client
from core.config import get_settings
import logging

logger = logging.getLogger(__name__)
app_config = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")



async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db_client = Depends(get_db_client)
):
    from services.user import UserService  # Import here to avoid circular import
    from dependencies.token import TokenBlacklistService
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    verification_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Email verification required",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check if token is blacklisted
    token_service = TokenBlacklistService(db_client)
    if await token_service.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        logger.debug(f"Attempting to decode token: {token[:10]}...") # Log first 10 chars
        payload = jwt.decode(token, app_config.SECRET_KEY, algorithms=[app_config.ALGORITHM])
        logger.debug(f"Token decoded successfully. Payload: {payload}") # Log payload

        user_id = payload.get("sub")
        logger.debug(f"Extracted user_id from 'sub' claim: {user_id}")

        if user_id is None:
            logger.warning("user_id ('sub' claim) not found in token payload.")
            raise credentials_exception

    except JWTError as e:
        logger.error(f"JWTError during token decoding: {e}") # Log specific JWT error
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error during token decoding/payload extraction: {e}")
        raise credentials_exception
    
    user_service = UserService(db_client)
    logger.debug(f"Looking up user with ID: {user_id}")
    user = await user_service.get_user_by_id(user_id)
    logger.debug(f"User lookup result: {'Found' if user else 'Not Found'}")

    if user is None:
        logger.warning(f"User with ID {user_id} not found in database.")
        raise credentials_exception

    # Check if user is verified
    if not user.get("is_verified", False):
        logger.warning(f"Access attempt by unverified user: {user.get('email')}")
        raise verification_exception

    logger.debug(f"Credentials validated successfully for user: {user.get('email')}")
    return user

async def get_current_user_optional_verification(
    token: str = Depends(oauth2_scheme),
    db_client = Depends(get_db_client)
):
    """
    Get current user without requiring email verification.
    Useful for endpoints that don't require full verification.
    """
    from services.user import UserService  # Import here to avoid circular import
    from dependencies.token import TokenBlacklistService
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check if token is blacklisted
    token_service = TokenBlacklistService(db_client)
    if await token_service.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(token, app_config.SECRET_KEY, algorithms=[app_config.ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError as e:
        logger.error(f"JWTError during token decoding: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error during token decoding/payload extraction: {e}")
        raise credentials_exception
    
    user_service = UserService(db_client)
    user = await user_service.get_user_by_id(user_id)

    if user is None:
        logger.warning(f"User with ID {user_id} not found in database.")
        raise credentials_exception

    return user

# def require_role(required_role: UserRole):
#     def role_dependency(current_user: dict = Depends(get_current_user)):
#         if current_user.role != required_role.value:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail=f"Access denied. Required role: {required_role.value}"
#             )
#         return current_user
#     return role_dependency

# async def get_admin_user(current_user = Depends(get_current_user)):
#     if current_user.role != UserRole.ADMIN:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Only admin users can access this resource"
#         )
#     return current_user

# async def get_advisor_user(current_user = Depends(get_current_user)):
#     if current_user.role != UserRole.ADVISOR:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Only advisor users can access this resource"
#         )
#     return current_user
