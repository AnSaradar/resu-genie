from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from bson.objectid import ObjectId

class Certification(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    user_id: ObjectId
    name: str = Field(..., description="Name of the certification")
    issuing_organization: str = Field(..., description="Organization that issued the certification")
    issue_date: date = Field(..., description="Date when the certification was issued")
    certificate_url: Optional[str] = Field(None, description="URL of the certification")
    description: Optional[str] = Field(None, description="Description of the certification")
    

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
