from pydantic import BaseModel, Field
from bson.objectid import ObjectId
from typing import Optional 

class Link(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    user_id: ObjectId
    website_name: str = Field(..., description="The name of the website")
    website_url: str = Field(..., description="URL of the website")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
