from pydantic import BaseModel
from typing import List
from app.schemas.atm import ATMOut


class RecommendationRequest(BaseModel):
    latitude: float
    longitude: float
    user_id: int | None = None
    needs_deposit: bool = False
    needs_currency: str | None = None  # e.g. "USD"


class RecommendationResponse(BaseModel):
    best_atm: ATMOut | None
    score: float
    reason: str
    alternatives: List[ATMOut] = []