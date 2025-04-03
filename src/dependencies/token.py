from datetime import datetime
from typing import Optional
from core.security import decode_access_token
import logging
from fastapi import Depends
from controllers.BaseController import BaseController
from .database import get_db_client

class TokenBlacklistService:
    def __init__(self, db_client: object):
        self.db_client = db_client
        self.collection = self.db_client.get_collection("token_blacklist")
        self.logger = logging.getLogger(__name__)
    
    async def blacklist_token(self, token: str) -> bool:
        """
        Add a token to the blacklist
        
        Args:
            token: JWT token to blacklist
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Decode token to get expiration time
            payload = decode_access_token(token)
            
            # Store token in blacklist
            await self.collection.insert_one({
                "token": token,
                "user_id": payload.get("user_id"),
                "expires_at": datetime.fromtimestamp(payload.get("exp")),
                "blacklisted_at": datetime.utcnow()
            })
            
            self.logger.info(f"Token blacklisted for user: {payload.get('user_id')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error blacklisting token: {str(e)}")
            return False
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """
        Check if a token is blacklisted
        
        Args:
            token: JWT token to check
            
        Returns:
            bool: True if blacklisted, False otherwise
        """
        try:
            result = await self.collection.find_one({"token": token})
            return result is not None
        except Exception as e:
            self.logger.error(f"Error checking blacklisted token: {str(e)}")
            return False
    
    async def cleanup_expired_tokens(self) -> int:
        """
        Remove expired tokens from the blacklist
        
        Returns:
            int: Number of tokens removed
        """
        try:
            result = await self.collection.delete_many({
                "expires_at": {"$lt": datetime.utcnow()}
            })
            
            self.logger.info(f"Cleaned up {result.deleted_count} expired tokens")
            return result.deleted_count
        except Exception as e:
            self.logger.error(f"Error cleaning up expired tokens: {str(e)}")
            return 0

def get_token_service(db_client = Depends(get_db_client)):
    return TokenBlacklistService(db_client)