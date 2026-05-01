"""
AI Recommendation engine.
Combines distance, ML availability prediction, user history affinity,
and service matching into a single weighted score.
"""

from sqlalchemy.orm import Session
from typing import Optional, List, Tuple
from app.services.atm_service import ATMService
from app.services.ml_model import AvailabilityModel
from app.models.history import UserHistory
from app.models.atm import ATM


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.atm_service = ATMService(db)
        self.model = AvailabilityModel()

    def _user_affinity(self, user_id: Optional[int], atm_id: int) -> float:
        """Boost score if user has used this ATM (or this bank's ATMs) before."""
        if not user_id:
            return 0.0

        count = (
            self.db.query(UserHistory)
            .filter(
                UserHistory.user_id == user_id,
                UserHistory.atm_id == atm_id
            )
            .count()
        )

        return min(0.3, 0.1 * count)  # cap affinity bonus

    def recommend(
        self,
        lat: float,
        lng: float,
        user_id: Optional[int] = None,
        needs_deposit: bool = False,
        needs_currency: Optional[str] = None,
        radius_km: float = 5.0,
        preferred_bank: Optional[str] = None,
    ) -> Tuple[Optional[ATM], float, str, List[ATM]]:

        candidates = self.atm_service.get_nearby(
            lat,
            lng,
            radius_km=radius_km,
            working_only=True,
            needs_deposit=needs_deposit,
            needs_currency=needs_currency,
        )

        if not candidates:
            return None, 0.0, "No ATMs match your criteria nearby.", []

        scored = []

        for atm in candidates:
            availability = self.model.predict_availability(atm)

            # distance normalized score (closer = better)
            dist_score = max(0.0, 1.0 - (atm.distance_km / radius_km))

            # user affinity
            affinity = self._user_affinity(user_id, atm.id)

            # bank preference
            bank_match = (
                1.0
                if (preferred_bank and atm.bank.lower() == preferred_bank.lower())
                else 0.0
            )

            # final weighted score
            final = (
                0.35 * availability +
                0.30 * dist_score +
                0.15 * (atm.rating / 5.0) +
                0.15 * bank_match +
                0.05 * affinity
            )

            scored.append((atm, final, availability))

        # sort by best score
        scored.sort(key=lambda x: x[1], reverse=True)

        best, best_score, best_avail = scored[0]

        bank_note = (
            " (your bank!)"
            if preferred_bank and best.bank.lower() == preferred_bank.lower()
            else ""
        )

        reason = (
            f"Best match{bank_note}: {best.distance_km} km away, "
            f"{int(best_avail * 100)}% predicted availability, "
            f"rating {best.rating}/5."
        )

        # top 3 alternatives
        alternatives = [s[0] for s in scored[1:4]]

        return best, round(best_score, 3), reason, alternatives