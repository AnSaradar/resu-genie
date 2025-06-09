from pydantic import BaseModel, Field, validator, EmailStr, model_validator
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import date
from enums import SeniorityLevel, Degree
from .common import Address, Certification, Language, Link, Skill
from dto.user_profile import UserProfileResponse
from dto.experiance import ExperienceResponse
from dto.education import EducationResponse
from dto.skill import SkillResponse
from dto.certification import CertificationResponse
from dto.language import LanguageResponse
from dto.link import LinkResponse
# class PersonalInfo(BaseModel):
#     name: str = Field(..., description="Full name of the individual")
#     email: EmailStr = Field(..., description="Email address")
#     phone: str = Field(..., description="Contact phone number")
#     current_job_title: Optional[str] = Field(None, description = "Current job title")
#     address: Optional[Address] = Field(None, description="Physical address of the individual")
#     linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
#     website: Optional[str] = Field(None, description="Personal website or portfolio URL")
#     date_of_birth: Optional[date] = Field(None, description="Date of birth")
#     profile_summary: Optional[str] = Field(None, description="Short summary about the individual")

# class Experience(BaseModel):

#     title: str = Field(..., description="Job title")
#     seniority_level: SeniorityLevel = Field(..., description="Seniority level of the job")
#     company: str = Field(..., description="Company name")
#     location: Optional[Address] = Field(None, description="Company Location")
#     start_date: date = Field(..., description="Start date of the job")
#     currently_working: bool = Field(..., description="Indicates if the person is currently working at this job")
#     end_date: Optional[date] = Field(
#         None, 
#         description="End date of the job, if applicable. Not required if 'currently_working' is True."
#     )
#     description: Optional[str] = Field(None, description="Description of job responsibilities and achievements")
    
#     @property
#     def is_active(self) -> bool:
#         """Helper property to determine if this is a current job."""
#         return self.currently_working

#     @property
#     def duration(self) -> str:
#         """Helper property to calculate the job duration as a string."""
#         if self.currently_working:
#             return f"From {self.start_date} to Present"
#         elif self.end_date:
#             return f"From {self.start_date} to {self.end_date}"
#         else:
#             return f"Started on {self.start_date}"


# class Education(BaseModel):
#     institution: str = Field(..., description="Name of the educational institution")
#     degree: Degree = Field(..., description="Degree obtained or pursued")
#     field: str = Field(..., description="Field of study (e.g., Information Technology Engineering)")
#     start_date: date = Field(..., description="Start date of the education program")
#     currently_studying: bool = Field(..., description="Indicates if the individual is still pursuing this degree")
#     end_date: Optional[date] = Field(None, description="End date of the education program, if applicable")
#     description: Optional[str] = Field(None, description="Details about the education program")

    

# class PersonalProject(BaseModel):
#     title: str = Field(..., description="The name of the project")
#     description: str = Field(..., description="A brief description of the project")
#     url: Optional[str] = Field(None, description="URL of the project's website or repository")

# class Resume(BaseModel):
#     personal_info: PersonalInfo
#     career_experiences: List[Experience] = Field(..., description="List of work experiences")
#     volunteering_experiences: List[Experience] = Field(..., description="List of volunteering experiences")
#     education: List[Education] = Field(..., description="List of educational qualifications")
#     technical_skills: List[Skill] = Field(..., description="List of Technical Skills")
#     soft_skills: List[Skill] = Field(..., description="List of Soft Skills")
#     certifications: Optional[List[Certification]] = Field(None, description="List of certifications")
#     languages: List[Language] = Field(..., description="List of languages known")
#     personal_projects: Optional[List[PersonalProject]] = Field(None, description="List of presonal projects")
#     personal_links: Optional[List[Link]] = Field(None, description="List of presonal links")


class Resume(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    user_id: ObjectId
    personal_info: UserProfileResponse
    career_experiences: List[ExperienceResponse] = Field(..., description="List of work experiences")
    volunteering_experiences: List[ExperienceResponse] = Field(..., description="List of volunteering experiences")
    education: List[EducationResponse] = Field(..., description="List of educational qualifications")
    technical_skills: List[SkillResponse] = Field(..., description="List of Technical Skills")
    soft_skills: List[SkillResponse] = Field(..., description="List of Soft Skills")
    certifications: Optional[List[CertificationResponse]] = Field(None, description="List of certifications")
    languages: List[LanguageResponse] = Field(..., description="List of languages known")
    personal_links: Optional[List[LinkResponse]] = Field(None, description="List of presonal links")
    personal_projects: Optional[List] = Field(None, description="List of presonal projects")
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
