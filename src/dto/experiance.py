from pydantic import BaseModel
from datetime import date
from typing import Optional
from schemas.common import Address
from enums import SeniorityLevel
from bson.objectid import ObjectId
from pydantic import Field
class ExperienceCreate(BaseModel):
    title: str
    seniority_level: SeniorityLevel
    company: str
    location: Optional[Address] = None
    start_date: date
    currently_working: bool
    end_date: Optional[date] = None
    description: Optional[str] = None
    is_volunteer: bool = Field(False, description="Indicates if the job is a volunteer position")
    

    class Config:
        from_attributes = True


class ExperienceUpdate(BaseModel):
    title: Optional[str] = None
    seniority_level: Optional[SeniorityLevel] = None
    company: Optional[str] = None
    location: Optional[Address] = None
    start_date: Optional[date] = None
    currently_working: Optional[bool] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    is_volunteer: bool = Field(False, description="Indicates if the job is a volunteer position")


    class Config:
        from_attributes = True

class ExperienceResponse(BaseModel):
    title: str
    seniority_level: SeniorityLevel
    company: str
    location: Optional[Address]
    start_date: date
    currently_working: bool
    end_date: Optional[date] = None
    description: Optional[str] = None
    is_active: bool
    duration: str
    is_volunteer: bool = Field(False, description="Indicates if the job is a volunteer position")


    class Config:
        from_attributes = True

