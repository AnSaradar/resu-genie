from motor.motor_asyncio import AsyncIOMotorClient
from core.config import  get_settings
import logging
from fastapi import Request


logger = logging.getLogger(__name__)
settings = get_settings()

def get_db_client(request: Request):
    """
    FastAPI dependency that returns the MongoDB database client
    established during app startup, avoiding new connections per request.
    """
    try:
        # Use the database client established during startup
        db_client = request.app.db_client
        return db_client
    except Exception as e:
        logger.error(f"Error accessing MongoDB client: {str(e)}")
        raise e
