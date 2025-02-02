from typing import Optional
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: str
    preferred_language: Optional[str] = None

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    preferred_language: Optional[str] = None

class UserResponse(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: str
    preferred_language: Optional[str]

class UserLogin(BaseModel):
    email: EmailStr
    password: str

