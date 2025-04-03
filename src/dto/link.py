from pydantic import BaseModel, Field
from typing import Optional, List

class LinkCreate(BaseModel):
    """
    DTO for creating a new link
    """
    website_name: str = Field(..., description="The name of the website")
    website_url: str = Field(..., description="URL of the website")

    class Config:
        from_attributes = True

class LinkUpdate(BaseModel):
    """
    DTO for updating an existing link
    """
    website_name: Optional[str] = Field(None, description="The name of the website")
    website_url: Optional[str] = Field(None, description="URL of the website")

    class Config:
        from_attributes = True

class LinkResponse(BaseModel):
    """
    DTO for link response
    """
    id: str = Field(..., alias="_id")
    website_name: str = Field(..., description="The name of the website")
    website_url: str = Field(..., description="URL of the website")

    class Config:
        from_attributes = True
        populate_by_name = True
