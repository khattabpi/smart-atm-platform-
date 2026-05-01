from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    atm_id = Column(Integer, ForeignKey("atms.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    issue_type = Column(String(50), nullable=False)  # not_working, missing_service, other
    description = Column(String(500))
    trust_weight = Column(Float, default=1.0)  # weight applied to user's report
    created_at = Column(DateTime(timezone=True), server_default=func.now())