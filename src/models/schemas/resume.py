from pydantic import BaseModel, Field, validator, EmailStr, model_validator
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import date
from models.enums import SeniorityLevel, Degree


class Address(BaseModel):
    city: str = Field(..., description="City of residence")
    country: str = Field(..., description="Country of residence")
    

class PersonalInfo(BaseModel):
    name: str = Field(..., description="Full name of the individual")
    email: EmailStr = Field(..., description="Email address")
    phone: str = Field(..., description="Contact phone number")
    address: Optional[Address] = Field(None, description="Physical address of the individual")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    website: Optional[str] = Field(None, description="Personal website or portfolio URL")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    profile_summary: Optional[str] = Field(None, description="Short summary about the individual")

class Experience(BaseModel):

    title: str = Field(..., description="Job title")
    seniority_level: SeniorityLevel = Field(..., description="Seniority level of the job")
    company: str = Field(..., description="Company name")
    start_date: date = Field(..., description="Start date of the job")
    currently_working: bool = Field(..., description="Indicates if the person is currently working at this job")
    end_date: Optional[date] = Field(
        None, 
        description="End date of the job, if applicable. Not required if 'currently_working' is True."
    )
    description: Optional[str] = Field(None, description="Description of job responsibilities and achievements")

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


class Education(BaseModel):
    institution: str = Field(..., description="Name of the educational institution")
    degree: Degree = Field(..., description="Degree obtained or pursued")
    field: str = Field(..., description="Field of study (e.g., Information Technology Engineering)")
    start_date: date = Field(..., description="Start date of the education program")
    currently_studying: bool = Field(..., description="Indicates if the individual is still pursuing this degree")
    end_date: Optional[date] = Field(None, description="End date of the education program, if applicable")
    description: Optional[str] = Field(None, description="Details about the education program")

        

class Certification(BaseModel):
    name: str = Field(..., description="Name of the certification")
    issuing_organization: str = Field(..., description="Organization that issued the certification")
    issue_date: date = Field(..., description="Date when the certification was issued")


class Summary(BaseModel):
    content: str = Field(..., description="Summary or objective statement")

class Language(BaseModel):
    name : str = Field(..., description="Name of the language")
    proficiency: str = Field(..., description="Proficiency of the language")

class Skill(BaseModel):
    name: str = Field(..., description="Name of the skill")
    proficiency: Optional[str] = Field(None, description="Proficiency level (e.g., Beginner, Intermediate, Advanced)")

class PersonalProject(BaseModel):
    title: str = Field(..., description="The name of the project")
    description: str = Field(..., description="A brief description of the project")
    url: Optional[str] = Field(None, description="URL of the project's website or repository")

class Resume(BaseModel):
    personal_info: PersonalInfo
    summary: Optional[Summary]
    carrer_experiences: List[Experience] = Field(..., description="List of work experiences")
    volunteering_experiences: List[Experience] = Field(..., description="List of work experiences")
    education: List[Education] = Field(..., description="List of educational qualifications")
    technical_skills: List[Skill] = Field(..., description="List of Technical Skills")
    soft_skills: List[Skill] = Field(..., description="List of Soft Skills")
    certifications: Optional[List[Certification]] = Field(None, description="List of certifications")
    languages: Optional[List[Language]] = Field(..., description="List of languages known")
    personal_projects: Optional[List[PersonalProject]] = Field(..., description="List of presonal projects")
        

