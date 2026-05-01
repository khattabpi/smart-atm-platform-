from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TransactionCreate(BaseModel):
    atm_id: Optional[int] = None
    type: str = Field(..., pattern="^(withdraw|deposit)$")
    amount: float = Field(..., gt=0)
    currency: str = "USD"
    note: Optional[str] = None


class TransactionOut(BaseModel):
    id: int
    type: str
    amount: float
    currency: str
    status: str
    note: Optional[str]
    atm_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True