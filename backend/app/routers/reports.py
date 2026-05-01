from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportOut
from app.services.atm_service import ATMService

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.post("/", response_model=ReportOut, status_code=201)
def submit_report(payload: ReportCreate, db: Session = Depends(get_db)):
    """User-submitted ATM issue report. Adjusts ATM reliability."""
    service = ATMService(db)
    if not service.get_by_id(payload.atm_id):
        raise HTTPException(status_code=404, detail="ATM not found")

    report = Report(**payload.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)

    service.update_reliability_after_report(payload.atm_id, payload.issue_type)
    return report


@router.get("/atm/{atm_id}", response_model=List[ReportOut])
def get_reports_for_atm(atm_id: int, db: Session = Depends(get_db)):
    return db.query(Report).filter(Report.atm_id == atm_id).all()