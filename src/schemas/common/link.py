from pydantic import BaseModel, Field

class Link(BaseModel):
    website_name: str = Field(..., description="The name of the website")
    website_url: str = Field(..., description="URL of the website")