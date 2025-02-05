from pydantic import BaseModel, Field
from typing import Optional

class Language(BaseModel):
    name : str = Field(..., description="Name of the language")
    proficiency: str = Field(..., description="Proficiency of the language")