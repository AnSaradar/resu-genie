from pydantic import BaseModel, Field, validator, EmailStr, model_validator
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import date, datetime
from enums import Degree

class Education(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    user_id: ObjectId
    institution: str = Field(..., description="Name of the educational institution")
    degree: Degree = Field(..., description="Degree obtained or pursued")
    field: str = Field(..., description="Field of study (e.g., Information Technology Engineering)")
    start_date: date = Field(..., description="Start date of the education program")
    currently_studying: bool = Field(..., description="Indicates if the individual is still pursuing this degree")
    end_date: Optional[date] = Field(None, description="End date of the education program, if applicable")
    description: Optional[str] = Field(None, description="Details about the education program")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}