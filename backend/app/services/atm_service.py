"""
Business logic for ATMs — querying, filtering, distance computation.
Keeping logic out of routers preserves clean architecture.
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.atm import ATM
from app.utils.geo import haversine_km


class ATMService:
    def __init__(self, db: Session):
        self.db = db

    def get_nearby(
        self,
        lat: float,
        lng: float,
        radius_km: float = 5.0,
        working_only: bool = False,
        needs_deposit: bool = False,
        needs_ewallet: bool = False,
        needs_currency: Optional[str] = None,
    ) -> List[ATM]:
        """Return ATMs within radius, sorted by distance, with optional filters."""
        query = self.db.query(ATM)

        if working_only:
            query = query.filter(ATM.is_working == True)
        if needs_deposit:
            query = query.filter(ATM.cash_deposit == True)
        if needs_ewallet:
            query = query.filter(ATM.ewallet_support == True)

        atms = query.all()
        results = []
        for atm in atms:
            d = haversine_km(lat, lng, atm.latitude, atm.longitude)
            if d <= radius_km:
                # Currency filter (JSON column → filter in Python for portability)
                if needs_currency and needs_currency.upper() not in (atm.supported_currencies or []):
                    continue
                atm.distance_km = round(d, 3)
                results.append(atm)

        results.sort(key=lambda a: a.distance_km)
        return results

    def get_by_id(self, atm_id: int) -> Optional[ATM]:
        return self.db.query(ATM).filter(ATM.id == atm_id).first()

    def update_reliability_after_report(self, atm_id: int, issue_type: str):
        """Decrease reliability score when negative reports are submitted."""
        atm = self.get_by_id(atm_id)
        if not atm:
            return
        delta = -0.1 if issue_type == "not_working" else -0.05
        atm.reliability_score = max(0.0, (atm.reliability_score or 1.0) + delta)
        # Auto-mark out of service if too many reports
        if atm.reliability_score < 0.3:
            atm.is_working = False
        self.db.commit()