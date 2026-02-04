from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    username: str
    email: EmailStr
    password: str
    phone: str
    address: str
    role: str  # "buyer" or "seller"


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response (without password)"""
    id: int
    username: str
    email: str
    phone: str
    address: str
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Schema for login response with token"""
    access_token: str
    token_type: str
    user: dict