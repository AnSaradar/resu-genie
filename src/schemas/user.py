from pydantic import BaseModel, Field, validator, EmailStr, model_validator
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import date, datetime

class User(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    preferred_language: Optional[str] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


