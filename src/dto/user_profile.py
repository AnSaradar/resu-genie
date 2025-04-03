from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from schemas.common import Address
from enums import WorkField

class UserProfileCreateUpdate(BaseModel):
    linkedin_url: Optional[str] = None
    website_url: Optional[str] = None
    birth_date: date
    profile_summary: Optional[str] = None
    address: Optional[Address] = None
    current_position: Optional[str] = Field(None, description="Current job position/title")
    work_field: Optional[WorkField] = Field(None, description="Primary field of work")
    years_of_experience: Optional[int] = Field(None, description="Total years of professional experience", ge=0, le=50)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        


class UserProfileResponse(BaseModel):
    linkedin_url: Optional[str] = None
    website_url: Optional[str] = None
    birth_date: date
    profile_summary: Optional[str] = None
    address: Optional[Address] = None
    current_position: Optional[str] = Field(None, description="Current job position/title")
    work_field: Optional[WorkField] = Field(None, description="Primary field of work")
    years_of_experience: Optional[int] = Field(None, description="Total years of professional experience")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        