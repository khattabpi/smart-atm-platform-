"""
Reports Router — handles crowdsourced ATM issue reports.
Publishes report.submitted event to RabbitMQ after DB commit.
"""
import asyncio
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportOut
from app.services.atm_service import ATMService

# Event bus integration (graceful — works even if broker is down)
try:
    from app.events.publisher import publish
    from app.events.schemas import EventType, ReportSubmittedPayload
    _EVENTS_AVAILABLE = True
except ImportError:
    _EVENTS_AVAILABLE = False


router = APIRouter(prefix="/api/reports", tags=["Reports"])


def _publish_report_event(report_id: int, atm_id: int, user_id, issue_type: str) -> None:
    """Bridge sync code → async publisher. Safe to call from BackgroundTasks."""
    if not _EVENTS_AVAILABLE:
        return
    try:
        asyncio.run(publish(
            EventType.REPORT_SUBMITTED,
            ReportSubmittedPayload(
                report_id=report_id,
                atm_id=atm_id,
                user_id=user_id,
                issue_type=issue_type,
            ).model_dump(),
        ))
    except Exception:
        pass  # Graceful — never fail the request because of broker issues


@router.post("/", response_model=ReportOut, status_code=201)
def submit_report(
    payload: ReportCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Submit a crowdsourced report about an ATM.
    Triggers async reliability decay + WebSocket broadcast via the event bus.
    """
    # 1. Decay reliability score immediately (sync — keeps API contract)
    service = ATMService(db)
    service.update_reliability_after_report(payload.atm_id, payload.issue_type)

    # 2. Persist the report
    report = Report(**payload.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)

    # 3. 🚀 Publish event AFTER successful commit (background — non-blocking)
    background_tasks.add_task(
        _publish_report_event,
        report.id,
        report.atm_id,
        getattr(report, "user_id", None),
        report.issue_type,
    )

    return report


@router.get("/atm/{atm_id}", response_model=List[ReportOut])
def get_reports_for_atm(atm_id: int, db: Session = Depends(get_db)):
    """List all reports for a specific ATM."""
    return db.query(Report).filter(Report.atm_id == atm_id).all()