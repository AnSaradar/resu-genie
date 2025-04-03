from typing import List, Optional
from fastapi import HTTPException
from bson import ObjectId
from core.security import get_password_hash
from schemas.user import User
from .base import BaseService
from enums import DataBaseCollectionNames
import logging
from dependencies import get_db_client
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient


class UserService(BaseService):
    def __init__(self, db_client : object):
        super().__init__(db_client = db_client)
        self.collection = self.db_client[DataBaseCollectionNames.USERS.value]
        self.logger = logging.getLogger(__name__)

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