from pydantic import BaseModel, Field
from typing import Optional

class Skill(BaseModel):
    name: str = Field(..., description="Name of the skill")
    proficiency: Optional[str] = Field(None, description="Proficiency level (e.g., Beginner, Intermediate, Advanced)")
