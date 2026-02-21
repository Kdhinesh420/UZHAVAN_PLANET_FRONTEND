from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.Feedback import Feedback
from models.User import User
from schemas.feedback import FeedbackCreate, FeedbackResponse
from auth import get_current_user, get_current_seller, oauth2_scheme
import models.Feedback as FeedbackModel

router = APIRouter(prefix="/feedback", tags=["Feedback"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    feedback_in: FeedbackCreate,
    db: Session = Depends(get_db),
    # Optional-a current_user-ai handle pannurom
    token: Optional[str] = Depends(oauth2_scheme)
):
    """
    Submit a new feedback (Public/Guest allowed)
    """
    current_user = None
    if token:
        try:
            from auth import decode_access_token
            payload = decode_access_token(token)
            if payload:
                user_id = payload.get("user_id")
                current_user = db.query(User).filter(User.id == user_id).first()
        except Exception:
            pass # Token invalid-naguest-a treat pannurom

    new_feedback = Feedback(
        user_id=current_user.id if current_user else None,
        username=feedback_in.name,
        email=feedback_in.email,
        rating=feedback_in.rating,
        comments=feedback_in.message
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback

@router.get("", response_model=List[FeedbackResponse])
def get_all_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_seller) # Only sellers/admins should see all feedback?
):
    """
    Get all feedback (Seller/Admin only)
    """
    return db.query(Feedback).order_by(Feedback.created_at.desc()).all()
