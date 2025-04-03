from typing import Optional
from pydantic import BaseModel, EmailStr, validator, Field
import re

class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password (minimum 8 characters)")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    phone: str = Field(..., description="User's phone number")
    preferred_language: Optional[str] = Field(None, description="User's preferred language")
    
    @validator('password')
    def password_strength(cls, v):
        """Validate that the password meets complexity requirements"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
            
        return v
    
    @validator('phone')
    def phone_format(cls, v):
        """Validate phone number format"""
        # Remove any non-digit characters for validation
        digits_only = re.sub(r'\D', '', v)
        
        # Check if the phone number has a reasonable length (adjust as needed)
        if len(digits_only) < 8 or len(digits_only) > 15:
            raise ValueError("Phone number must be between 8 and 15 digits")
            
        return v  # Return original value to preserve formatting

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    preferred_language: Optional[str] = None
    
    @validator('phone')
    def phone_format(cls, v):
        """Validate phone number format if provided"""
        if v is None:
            return v
            
        # Remove any non-digit characters for validation
        digits_only = re.sub(r'\D', '', v)
        
        # Check if the phone number has a reasonable length
        if len(digits_only) < 8 or len(digits_only) > 15:
            raise ValueError("Phone number must be between 8 and 15 digits")
            
        return v  # Return original value to preserve formatting

class UserResponse(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: str
    preferred_language: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

