"""
Simple ML scoring model — predicts probability that an ATM is currently available.
Uses logistic-regression-style weighted scoring; trained features are heuristic
but the structure is ready for a real sklearn model trained on historical data.
"""
import numpy as np
from datetime import datetime
from app.models.atm import ATM


class AvailabilityModel:
    """
    Scores ATM availability between 0 and 1 using weighted features:
      - reliability_score
      - rating
      - is_working flag
      - time-of-day factor (banks/malls open hours have higher availability)
    """
    # Trained-style coefficients (could be replaced with sklearn .pkl)
    WEIGHTS = {
        "reliability": 2.5,
        "rating": 0.4,
        "is_working": 3.0,
        "time_factor": 1.0,
        "bias": -2.0,
    }

    def _time_factor(self) -> float:
        """Return [0..1] based on hour of day; ATMs more reliable during business hours."""
        hour = datetime.now().hour
        if 8 <= hour <= 22:
            return 1.0
        if 6 <= hour < 8 or 22 < hour <= 24:
            return 0.7
        return 0.5  # late night

    @staticmethod
    def _sigmoid(x: float) -> float:
        return 1.0 / (1.0 + np.exp(-x))

    def predict_availability(self, atm: ATM) -> float:
        w = self.WEIGHTS
        z = (
            w["reliability"] * (atm.reliability_score or 0)
            + w["rating"] * (atm.rating or 0)
            + w["is_working"] * (1.0 if atm.is_working else 0.0)
            + w["time_factor"] * self._time_factor()
            + w["bias"]
        )
        return float(self._sigmoid(z))