from pydantic import BaseModel, Field, validator, EmailStr, model_validator
from typing import List, Optional
from bson.objectid import ObjectId
from enums import SkillProficiency

class Skill(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    user_id: ObjectId
    name: str = Field(..., description="Name of the skill")
    proficiency: Optional[SkillProficiency] = Field(None, description="Proficiency level (e.g., Beginner, Intermediate, Advanced)")
    is_soft_skill: bool = Field(False, description="Indicates if the skill is a soft skill")

    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}



