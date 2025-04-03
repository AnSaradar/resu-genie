from pydantic import BaseModel, Field, validator, EmailStr, model_validator
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import date, datetime
from schemas.common import Address
from enums import WorkField

class UserProfile(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    user_id: ObjectId
    linkedin_url: Optional[str]
    website_url: Optional[str]
    birth_date: date
    profile_summary: Optional[str]
    address: Optional[Address]
    current_position: Optional[str] = Field(None, description="Current job position/title")
    work_field: Optional[WorkField] = Field(None, description="Primary field of work")
    years_of_experience: Optional[int] = Field(None, description="Total years of professional experience", ge=0, le=50)
    
    @validator("user_id", pre=True)
    def validate_object_id(cls, value):
        """Converts a string into an ObjectId."""
        if isinstance(value, str):
            try:
                return ObjectId(value)  # Convert string to ObjectId
            except Exception:
                raise ValueError("Invalid ObjectId format")
        return value

    @validator("years_of_experience")
    def validate_years_of_experience(cls, v):
        """Validate that years_of_experience is within a reasonable range."""
        if v is not None and (v < 0 or v > 50):
            raise ValueError("Years of experience must be between 0 and 50")
        return v
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


