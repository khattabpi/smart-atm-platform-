"""Event payload contracts — versioned & strictly typed."""
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
from uuid import uuid4


class EventType(str, Enum):
    REPORT_SUBMITTED = "report.submitted"
    ATM_STATUS_CHANGED = "atm.status_changed"
    TRANSACTION_COMPLETED = "transaction.completed"
    USER_REGISTERED = "user.registered"


class Event(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: EventType
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1
    payload: dict[str, Any]


# Strongly-typed payloads
class ReportSubmittedPayload(BaseModel):
    report_id: int
    atm_id: int
    user_id: int | None
    issue_type: str


class AtmStatusChangedPayload(BaseModel):
    atm_id: int
    is_working: bool
    reliability: float


class TransactionCompletedPayload(BaseModel):
    transaction_id: int
    user_id: int
    type: str
    amount: float


class UserRegisteredPayload(BaseModel):
    user_id: int
    email: str