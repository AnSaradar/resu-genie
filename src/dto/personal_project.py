from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List

class PersonalProjectCreate(BaseModel):
    title: str = Field(..., description="The name of the project")
    description: str = Field(..., description="A brief description of the project")
    technologies: Optional[List[str]] = Field(None, description="List of technologies used in the project")
    start_date: Optional[date] = Field(None, description="Start date of the project")
    end_date: Optional[date] = Field(None, description="End date of the project, if applicable")
    is_ongoing: bool = Field(False, description="Indicates if the project is still ongoing")
    url: Optional[str] = Field(None, description="URL of the project's website or repository")
    repository_url: Optional[str] = Field(None, description="URL of the project's repository (e.g., GitHub)")

    class Config:
        from_attributes = True

class PersonalProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, description="The name of the project")
    description: Optional[str] = Field(None, description="A brief description of the project")
    technologies: Optional[List[str]] = Field(None, description="List of technologies used in the project")
    start_date: Optional[date] = Field(None, description="Start date of the project")
    end_date: Optional[date] = Field(None, description="End date of the project, if applicable")
    is_ongoing: Optional[bool] = Field(None, description="Indicates if the project is still ongoing")
    url: Optional[str] = Field(None, description="URL of the project's website or repository")
    repository_url: Optional[str] = Field(None, description="URL of the project's repository (e.g., GitHub)")

    class Config:
        from_attributes = True

class PersonalProjectResponse(BaseModel):
    id: str = Field(..., alias="_id")
    title: str = Field(..., description="The name of the project")
    description: str = Field(..., description="A brief description of the project")
    technologies: Optional[List[str]] = Field(None, description="List of technologies used in the project")
    start_date: Optional[date] = Field(None, description="Start date of the project")
    end_date: Optional[date] = Field(None, description="End date of the project, if applicable")
    is_ongoing: bool = Field(False, description="Indicates if the project is still ongoing")
    url: Optional[str] = Field(None, description="URL of the project's website or repository")
    repository_url: Optional[str] = Field(None, description="URL of the project's repository (e.g., GitHub)")
    duration: Optional[str] = Field(None, description="Duration of project (e.g., '6 months')")

    class Config:
        from_attributes = True
        populate_by_name = True 