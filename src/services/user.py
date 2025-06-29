from typing import List, Optional
from fastapi import HTTPException
from bson import ObjectId
from core.security import get_password_hash
from schemas.user import User
from .base import BaseService
from enums import DataBaseCollectionNames, ResponseSignal
import logging
from dependencies import get_db_client
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime


class UserService(BaseService):
    def __init__(self, db_client : object):
        super().__init__(db_client = db_client)
        self.collection = self.db_client[DataBaseCollectionNames.USERS.value]
        self.logger = logging.getLogger(__name__)

    async def create_user_with_verification(self, user_data: User) -> dict:
        """
        Create a new user with email verification required.
        If user exists but is not verified, allow re-registration.
        """
        try:
            # Check if user email already exists
            existing_user = await self.collection.find_one({"email": user_data.email})
            
            if existing_user:
                if existing_user.get("is_verified", False):
                    # User exists and is verified
                    self.logger.warning(f"Registration attempt with verified email: {user_data.email}")
                    raise HTTPException(status_code=409, detail=ResponseSignal.EMAIL_ALREADY_REGISTERED.value)
                else:
                    # User exists but is not verified - update the record
                    user_dict = user_data.dict()
                    user_dict["password"] = get_password_hash(user_dict["password"])
                    user_dict["is_verified"] = False
                    user_dict["updated_at"] = datetime.utcnow()
                    
                    await self.collection.update_one(
                        {"email": user_data.email},
                        {"$set": user_dict}
                    )
                    
                    updated_user = await self.collection.find_one({"email": user_data.email})
                    self.logger.info(f"Updated unverified user: {user_data.email}")
                    return updated_user
            
            # Check if phone number already exists for verified users
            existing_phone = await self.collection.find_one({"phone": user_data.phone, "is_verified": True})
            if existing_phone:
                self.logger.warning(f"Registration attempt with verified phone: {user_data.phone}")
                raise HTTPException(status_code=409, detail=ResponseSignal.PHONE_ALREADY_REGISTERED.value)
            
            # Create new user
            user_dict = user_data.dict()
            user_dict["password"] = get_password_hash(user_dict["password"])
            user_dict["is_verified"] = False
            user_dict["created_at"] = datetime.utcnow()
            
            # Insert user
            result = await self.collection.insert_one(user_dict)
            user_dict["_id"] = result.inserted_id
            
            self.logger.info(f"Created new unverified user: {user_data.email}")
            return user_dict
        
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error creating user with verification: {str(e)}")
            raise HTTPException(status_code=500, detail=ResponseSignal.REGISTRATION_SERVER_ERROR.value)

    async def verify_user_email(self, email: str) -> bool:
        """Mark user as verified after successful OTP verification"""
        try:
            result = await self.collection.update_one(
                {"email": email, "is_verified": False},
                {"$set": {"is_verified": True, "verified_at": datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                self.logger.info(f"User email verified successfully: {email}")
                return True
            else:
                self.logger.warning(f"No unverified user found for email: {email}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error verifying user email: {str(e)}")
            return False

    async def is_user_verified(self, email: str) -> bool:
        """Check if user is verified"""
        try:
            user = await self.collection.find_one({"email": email})
            return user.get("is_verified", False) if user else False
        except Exception as e:
            self.logger.error(f"Error checking user verification status: {str(e)}")
            return False

    async def create_user(self, user_data: User) -> dict:
        # Check if user email already exists
        if await self.collection.find_one({"email": user_data.email}):
            self.logger.warning(f"Registration attempt with existing email: {user_data.email}")
            raise HTTPException(status_code=409, detail="Email already registered")
        
        # Check if phone number already exists
        if await self.collection.find_one({"phone": user_data.phone}):
            self.logger.warning(f"Registration attempt with existing phone: {user_data.phone}")
            raise HTTPException(status_code=409, detail="Phone number already registered")
        
        try:
            # Hash password
            user_dict = user_data.dict()
            user_dict["password"] = get_password_hash(user_dict["password"])
            
            # Insert user
            result = await self.collection.insert_one(user_dict)
            user_dict["_id"] = result.inserted_id
            return user_dict
        
        except Exception as e:
            self.logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(status_code=500, detail="Server error during registration")

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        user = await self.collection.find_one({"email": email})
        return user

    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        return user

    async def update_user(self, user_id: str, update_data: dict) -> Optional[dict]:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        if update_data:
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            if result.modified_count:
                return await self.get_user_by_id(user_id)
        return None

def get_user_service(db_client: AsyncIOMotorClient = Depends(get_db_client)):
    return UserService(db_client)