from pydantic import BaseModel, Field
from datetime import date
from typing import Optional
from enums import Degree
 

class EducationCreate(BaseModel):

    institution: str = Field(..., description="Name of the educational institution")
    degree: Degree = Field(..., description="Degree obtained or pursued")
    field: str = Field(..., description="Field of study (e.g., Information Technology Engineering)")
    start_date: date = Field(..., description="Start date of the education program")
    currently_studying: bool = Field(..., description="Indicates if the individual is still pursuing this degree")
    end_date: Optional[date] = Field(None, description="End date of the education program, if applicable")
    description: Optional[str] = Field(None, description="Details about the education program")

    class Config:
        from_attributes = True

class EducationUpdate(BaseModel):

    institution: Optional[str] = Field(None, description="Name of the educational institution")
    degree: Optional[Degree] = Field(None, description="Degree obtained or pursued")
    field: Optional[str] = Field(None, description="Field of study (e.g., Information Technology Engineering)")
    start_date: Optional[date] = Field(None, description="Start date of the education program")
    currently_studying: Optional[bool] = Field(None, description="Indicates if the individual is still pursuing this degree")
    end_date: Optional[date] = Field(None, description="End date of the education program, if applicable")
    description: Optional[str] = Field(None, description="Details about the education program")

    class Config:
        from_attributes = True

class EducationResponse(BaseModel):
    id: str = Field(..., alias="_id")
    institution: str = Field(..., description="Name of the educational institution")
    degree: Degree = Field(..., description="Degree obtained or pursued")
    field: str = Field(..., description="Field of study")
    start_date: date = Field(..., description="Start date of the education program")
    currently_studying: bool = Field(..., description="Indicates if the individual is still pursuing this degree")
    end_date: Optional[date] = Field(None, description="End date of the education program, if applicable")
    description: Optional[str] = Field(None, description="Details about the education program")
    duration: str = Field(..., description="Duration of education (e.g., '2 years 3 months')")

    class Config:
        from_attributes = True
        populate_by_name = True




