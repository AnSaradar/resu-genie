from pydantic import BaseModel, Field
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import date, datetime

class PersonalProject(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    user_id: ObjectId
    title: str = Field(..., description="The name of the project")
    description: str = Field(..., description="A brief description of the project")
    technologies: Optional[List[str]] = Field(None, description="List of technologies used in the project")
    start_date: Optional[date] = Field(None, description="Start date of the project")
    end_date: Optional[date] = Field(None, description="End date of the project, if applicable")
    is_ongoing: bool = Field(False, description="Indicates if the project is still ongoing")
    url: Optional[str] = Field(None, description="URL of the project's website or repository")
    repository_url: Optional[str] = Field(None, description="URL of the project's repository (e.g., GitHub)")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str} 