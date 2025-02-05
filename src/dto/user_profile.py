from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from schemas.common import Address

class UserProfileCreateUpdate(BaseModel):
    linkedin_url: Optional[str]
    website_url: Optional[str]
    birth_date: date
    profile_summary: Optional[str]
    address: Optional[Address]

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        


class UserProfileResponse(BaseModel):
    linkedin_url: Optional[str]
    website_url: Optional[str]
    birth_date: date
    profile_summary: Optional[str]
    address: Optional[Address]

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        