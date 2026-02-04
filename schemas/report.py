from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReportCreate(BaseModel):
    order_id: Optional[str] = None
    issue_type: str
    subject: str
    description: str

class ReportResponse(BaseModel):
    id: int
    user_id: int
    order_id: Optional[str]
    issue_type: str
    subject: str
    description: str
    status: str
    created_at: datetime
    username: Optional[str] = None

    class Config:
        from_attributes = True
