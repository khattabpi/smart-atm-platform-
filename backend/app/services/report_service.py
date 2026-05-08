from sqlalchemy.orm import Session
from app.models.report import Report
from app.events.publisher import publish
from app.events.schemas import EventType, ReportSubmittedPayload


class ReportService:
    def __init__(self, db: Session):
        self.db = db

    async def submit(self, atm_id: int, user_id: int | None, issue_type: str, description: str) -> Report:
        report = Report(
            atm_id=atm_id, user_id=user_id, issue_type=issue_type, description=description
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        # 🚀 Publish AFTER commit — reliability decay handled by worker
        await publish(
            EventType.REPORT_SUBMITTED,
            ReportSubmittedPayload(
                report_id=report.id,
                atm_id=atm_id,
                user_id=user_id,
                issue_type=issue_type,
            ).model_dump(),
        )
        return report