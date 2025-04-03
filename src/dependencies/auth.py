from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional
from dependencies.database import get_db_client
from core.config import get_settings

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
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user_service = UserService(db_client)
    user = await user_service.get_user_by_id(user_id)
    if user is None:
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
