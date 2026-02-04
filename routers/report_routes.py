from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.User import User
from models.Report import Report
from schemas.report import ReportCreate, ReportResponse
from dependencies import get_db
from auth import get_current_user, get_current_seller, get_current_buyer

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    report_in: ReportCreate,
    current_user: User = Depends(get_current_buyer),
    db: Session = Depends(get_db)
):
    """
    Submit a new report (Buyer only)
    """
    new_report = Report(
        user_id=current_user.id,
        order_id=report_in.order_id,
        issue_type=report_in.issue_type,
        subject=report_in.subject,
        description=report_in.description
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report

@router.get("/my-reports", response_model=List[ReportResponse])
def get_my_reports(
    current_user: User = Depends(get_current_buyer),
    db: Session = Depends(get_db)
):
    """
    Get all reports submitted by the current user
    """
    return db.query(Report).filter(Report.user_id == current_user.id).order_by(Report.created_at.desc()).all()

@router.get("/seller", response_model=List[ReportResponse])
def get_seller_reports(
    current_user: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """
    Get reports related to seller's orders (Seller only)
    For simplicity, return all reports for now. In a real app,
    we'd filter reports based on the order's seller.
    """
    # Simple logic: Return all reports since we don't have a direct 
    # link between report and product/seller except via order_id string.
    # In a production app, we'd join Report -> Order -> OrderItem -> Product -> Seller
    
    # Let's try to be a bit more specific by joining with orders
    reports = db.query(Report).all()
    
    # Enrich with username
    result = []
    for r in reports:
        user = db.query(User).filter(User.id == r.user_id).first()
        r_dict = {
            "id": r.id,
            "user_id": r.user_id,
            "order_id": r.order_id,
            "issue_type": r.issue_type,
            "subject": r.subject,
            "description": r.description,
            "status": r.status,
            "created_at": r.created_at,
            "username": user.username if user else "Unknown"
        }
        result.append(r_dict)
        
    return result

@router.put("/{report_id}/status", response_model=ReportResponse)
def update_report_status(
    report_id: int,
    status: str,
    current_user: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """
    Sellers can mark reports as resolved or closed
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report.status = status
    db.commit()
    db.refresh(report)
    return report
