from pydantic import BaseModel, Field
from typing import Optional, List
from enums import SkillProficiency

class SkillCreate(BaseModel):
    """
    DTO for creating a new skill
    """
    name: str = Field(..., description="Name of the skill")
    proficiency: Optional[SkillProficiency] = Field(None, description="Proficiency level (e.g., Beginner, Intermediate, Advanced)")
    is_soft_skill: bool = Field(False, description="Indicates if the skill is a soft skill")
    class Config:
        from_attributes = True

class SkillUpdate(BaseModel):
    """
    DTO for updating an existing skill
    """
    name: Optional[str] = Field(None, description="Name of the skill")
    proficiency: Optional[SkillProficiency] = Field(None, description="Proficiency level (e.g., Beginner, Intermediate, Advanced)")

    class Config:
        from_attributes = True

class SkillResponse(BaseModel):
    """
    DTO for skill response
    """
    id: str = Field(..., alias="_id")
    name: str = Field(..., description="Name of the skill")
    proficiency: Optional[SkillProficiency] = Field(None, description="Proficiency level (e.g., Beginner, Intermediate, Advanced)")
    is_soft_skill: bool = Field(False, description="Indicates if the skill is a soft skill")
    
    class Config:
        from_attributes = True
        populate_by_name = True

class SkillsGroupResponse(BaseModel):
    """
    DTO for grouped skills response
    """
    category: str = Field(..., description="Category or group name for the skills")
    skills: List[SkillResponse] = Field(..., description="List of skills in this category")

    class Config:
        from_attributes = True
