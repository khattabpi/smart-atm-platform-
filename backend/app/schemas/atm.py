from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ATMBase(BaseModel):
    name: str
    bank: str
    address: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    cash_withdrawal: bool = True
    cash_deposit: bool = False
    ewallet_support: bool = False
    currency_exchange: bool = False
    supported_currencies: List[str] = []
    is_working: bool = True


class ATMCreate(ATMBase):
    pass


class ATMOut(ATMBase):
    id: int
    rating: float
    reliability_score: float
    last_updated: datetime
    distance_km: Optional[float] = None  # populated when querying nearby

    class Config:
        from_attributes = True