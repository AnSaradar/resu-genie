from pydantic import BaseModel, Field
from typing import Optional
from bson.objectid import ObjectId
from enums import LanguageProficiency

class Language(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    user_id: ObjectId
    name : str = Field(..., description="Name of the language")
    proficiency: LanguageProficiency = Field(..., description="Proficiency of the language")
    is_native: bool = Field(default=False, description="Whether this is a native language")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

