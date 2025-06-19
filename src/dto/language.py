from pydantic import BaseModel, Field
from typing import Optional, List
from enums import LanguageProficiency

class LanguageCreate(BaseModel):
    """
    DTO for creating a new language
    """
    name: str = Field(..., description="Name of the language")
    proficiency: LanguageProficiency = Field(..., description="Proficiency of the language")
    is_native: Optional[bool] = Field(default=False, description="Whether this is a native language")

    class Config:
        from_attributes = True

class LanguageUpdate(BaseModel):
    """
    DTO for updating an existing language
    """
    name: Optional[str] = Field(None, description="Name of the language")
    proficiency: Optional[LanguageProficiency] = Field(None, description="Proficiency of the language")
    is_native: Optional[bool] = Field(None, description="Whether this is a native language")

    class Config:
        from_attributes = True

class LanguageResponse(BaseModel):
    """
    DTO for language response
    """
    id: str = Field(..., alias="_id")
    name: str = Field(..., description="Name of the language")
    proficiency: LanguageProficiency = Field(..., description="Proficiency of the language")
    is_native: bool = Field(default=False, description="Whether this is a native language")

    class Config:
        from_attributes = True
        populate_by_name = True

class LanguagesGroupResponse(BaseModel):
    """
    DTO for grouped languages response
    """
    proficiency_level: str = Field(..., description="Proficiency level of the languages")
    languages: List[LanguageResponse] = Field(..., description="List of languages with this proficiency level")

    class Config:
        from_attributes = True

