from pydantic import BaseModel, Field, validator, EmailStr, model_validator
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import date, datetime
from schemas.common import Address
from enums import SeniorityLevel
class Experience(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    user_id: ObjectId
    title: str = Field(..., description="Job title")
    seniority_level: SeniorityLevel = Field(..., description="Seniority level of the job")
    company: str = Field(..., description="Company name")
    location: Optional[Address] = Field(None, description="Company Location")
    start_date: date = Field(..., description="Start date of the job")
    currently_working: bool = Field(..., description="Indicates if the person is currently working at this job")
    end_date: Optional[date] = Field(
        None, 
        description="End date of the job, if applicable. Not required if 'currently_working' is True."
    )
    description: Optional[str] = Field(None, description="Description of job responsibilities and achievements")
    is_volunteer: bool = Field(False, description="Indicates if the job is a volunteer position")
    @property
    def is_active(self) -> bool:
        """Helper property to determine if this is a current job."""
        return self.currently_working

    @property
    def duration(self) -> str:
        """Helper property to calculate the job duration as a string."""
        if self.currently_working:
            return f"From {self.start_date} to Present"
        elif self.end_date:
            return f"From {self.start_date} to {self.end_date}"
        else:
            return f"Started on {self.start_date}"
        
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}