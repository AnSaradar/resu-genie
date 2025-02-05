from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
class Certification(BaseModel):
    name: str = Field(..., description="Name of the certification")
    issuing_organization: str = Field(..., description="Organization that issued the certification")
    issue_date: date = Field(..., description="Date when the certification was issued")
