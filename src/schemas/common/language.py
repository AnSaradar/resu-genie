from pydantic import BaseModel, Field
from typing import Optional

class Language(BaseModel):
    name : str = Field(..., description="Name of the language")
    proficiency: str = Field(..., description="Proficiency of the language")
    is_native: Optional[bool] = Field(default=False, description="Whether this is a native language")