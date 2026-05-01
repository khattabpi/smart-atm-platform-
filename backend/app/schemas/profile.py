from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProfileOut(BaseModel):
    user_id: int
    full_name: Optional[str]
    email: str
    bank: Optional[str]
    preferred_currency: str
    simulated_balance: float
    phone: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    bank: Optional[str] = None
    preferred_currency: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None