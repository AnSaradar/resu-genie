from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class OTPRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    purpose: str = Field(default="verification", description="Purpose of OTP (verification, password-reset, etc.)")

class OTPVerification(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")
    purpose: str = Field(default="verification", description="Purpose of OTP verification")

class OTPResponse(BaseModel):
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    expires_at: Optional[datetime] = Field(None, description="OTP expiration timestamp")
    
    class Config:
        from_attributes = True 