from pydantic import BaseModel, Field, validator, EmailStr, model_validator
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import date, datetime
from schemas.common import Address
class UserProfileSchema(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    user_id: ObjectId
    linkedin_url: Optional[str]
    website_url: Optional[str]
    birth_date: date
    profile_summary: Optional[str]
    address: Optional[Address]
    
    @validator("user_id", pre=True)
    def validate_object_id(cls, value):
        """Converts a string into an ObjectId."""
        if isinstance(value, str):
            try:
                return ObjectId(value)  # Convert string to ObjectId
            except Exception:
                raise ValueError("Invalid ObjectId format")
        return value
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


