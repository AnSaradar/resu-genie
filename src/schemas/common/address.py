from pydantic import BaseModel, Field
from typing import Optional

class Address(BaseModel):
    city: Optional[str] = Field(None, description="City of residence")
    country: str = Field(..., description="Country of residence")