from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class FeedbackCreate(BaseModel):
    name: str
    email: str
    rating: int
    message: str
    subject: Optional[str] = "General Feedback"

class FeedbackResponse(BaseModel):
    id: int
    user_id: Optional[int]
    username: str
    email: str
    rating: int
    comments: str
    created_at: datetime

    class Config:
        from_attributes = True
