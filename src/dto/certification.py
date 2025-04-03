from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class CertificationCreate(BaseModel):
    """
    DTO for creating a new certification
    """
    name: str = Field(..., description="Name of the certification")
    issuing_organization: str = Field(..., description="Organization that issued the certification")
    issue_date: date = Field(..., description="Date when the certification was issued")

    class Config:
        from_attributes = True

class CertificationUpdate(BaseModel):
    """
    DTO for updating an existing certification
    """
    name: Optional[str] = Field(None, description="Name of the certification")
    issuing_organization: Optional[str] = Field(None, description="Organization that issued the certification")
    issue_date: Optional[date] = Field(None, description="Date when the certification was issued")

    class Config:
        from_attributes = True

class CertificationResponse(BaseModel):
    """
    DTO for certification response
    """
    id: str = Field(..., alias="_id")
    name: str = Field(..., description="Name of the certification")
    issuing_organization: str = Field(..., description="Organization that issued the certification")
    issue_date: date = Field(..., description="Date when the certification was issued")

    class Config:
        from_attributes = True
        populate_by_name = True
