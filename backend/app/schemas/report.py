from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReportCreate(BaseModel):
    atm_id: int
    user_id: Optional[int] = None
    issue_type: str  # not_working | missing_service | other
    description: Optional[str] = None


class ReportOut(BaseModel):
    id: int
    atm_id: int
    issue_type: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True