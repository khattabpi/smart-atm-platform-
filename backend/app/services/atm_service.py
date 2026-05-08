"""
ATM Service — synchronous business logic.
Drop-in compatible with the existing sync routers.
Handles both `lat/lng` and `latitude/longitude` field naming defensively.
"""
import json
import asyncio
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.atm import ATM
from app.utils.geo import haversine_km

# Optional cache imports — graceful degradation
try:
    from app.cache.redis_client import get_redis
    from app.cache.keys import CacheKeys
    from app.core.logging import get_logger
    _CACHE_AVAILABLE = True
    logger = get_logger(__name__)
except ImportError:
    _CACHE_AVAILABLE = False
    logger = None


# ============================================================================
# Helpers
# ============================================================================
def _atm_lat(atm: ATM) -> Optional[float]:
    """Read latitude from whichever field exists."""
    val = getattr(atm, "latitude", None)
    if val is None:
        val = getattr(atm, "lat", None)
    return float(val) if val is not None else None


def _atm_lng(atm: ATM) -> Optional[float]:
    """Read longitude from whichever field exists."""
    val = getattr(atm, "longitude", None)
    if val is None:
        val = getattr(atm, "lng", None)
    return float(val) if val is not None else None


def _run_async(coro):
    """Execute an async coroutine from sync context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return None
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


def _cache_invalidate(*keys: str) -> None:
    """Best-effort cache invalidation."""
    if not _CACHE_AVAILABLE or not keys:
        return
    r = get_redis()
    if not r:
        return
    try:
        async def _del():
            try:
                await r.delete(*keys)
            except Exception:
                pass
        try:
            asyncio.run(_del())
        except RuntimeError:
            pass
    except Exception:
        pass


# ============================================================================
# ATM Service
# ============================================================================
class ATMService:
    """Synchronous ATM service. Matches existing router contracts."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------------
    # Read — single ATM
    # ------------------------------------------------------------------------
    def get_by_id(self, atm_id: int) -> Optional[ATM]:
        return self.db.query(ATM).filter(ATM.id == atm_id).first()

    # ------------------------------------------------------------------------
    # Read — nearby ATMs
    # ------------------------------------------------------------------------
    def get_nearby(
        self,
        lat: float,
        lng: float,
        radius_km: float = 5.0,
        working_only: bool = False,
        needs_deposit: bool = False,
        needs_ewallet: bool = False,
        currency: Optional[str] = None,
        # Aliases — accept alternate kwargs used elsewhere in the codebase
        needs_currency: Optional[str] = None,
    ) -> List[ATM]:
        """
        Returns ATMs within radius_km, ordered by distance.
        Handles both lat/lng and latitude/longitude field conventions.
        """
        # Coalesce aliases
        if currency is None and needs_currency is not None:
            currency = needs_currency

        q = self.db.query(ATM)

        if working_only:
            q = q.filter(ATM.is_working == True)  # noqa: E712

        # Filter by services if the columns exist
        if needs_deposit and hasattr(ATM, "cash_deposit"):
            q = q.filter(ATM.cash_deposit == True)  # noqa: E712
        elif needs_deposit and hasattr(ATM, "supports_deposit"):
            q = q.filter(ATM.supports_deposit == True)  # noqa: E712

        if needs_ewallet and hasattr(ATM, "ewallet_support"):
            q = q.filter(ATM.ewallet_support == True)  # noqa: E712
        elif needs_ewallet and hasattr(ATM, "supports_ewallet"):
            q = q.filter(ATM.supports_ewallet == True)  # noqa: E712

        atms = q.all()

        # Filter by distance + currency in Python
        results = []
        for atm in atms:
            atm_lat = _atm_lat(atm)
            atm_lng = _atm_lng(atm)
            if atm_lat is None or atm_lng is None:
                continue

            distance = haversine_km(lat, lng, atm_lat, atm_lng)
            if distance > radius_km:
                continue

            if currency:
                supported = getattr(atm, "supported_currencies", None)
                if supported is None:
                    supported = []

                # Handle both list (JSON) and string types
                if isinstance(supported, str):
                    if currency not in supported:
                        continue
                elif isinstance(supported, (list, tuple)):
                    if currency not in supported:
                        continue

            results.append((distance, atm))

        # ✅ FIXED PART
        results.sort(key=lambda x: x[0])
        out = []
        for dist, atm in results:
            # Transient attribute — Pydantic's from_attributes=True will pick it up
            atm.distance_km = round(dist, 3)
            out.append(atm)

        return out

    # ------------------------------------------------------------------------
    # Write — update ATM status
    # ------------------------------------------------------------------------
    def update_status(self, atm_id: int, is_working: bool) -> Optional[ATM]:
        atm = self.db.query(ATM).filter(ATM.id == atm_id).first()
        if not atm:
            return None
        atm.is_working = is_working
        self.db.commit()
        self.db.refresh(atm)

        if _CACHE_AVAILABLE:
            try:
                _cache_invalidate(CacheKeys.atm_detail(atm_id))
            except Exception:
                pass

        return atm

    # ------------------------------------------------------------------------
    # Crowdsourcing — reliability decay after a user report
    # ------------------------------------------------------------------------
    def update_reliability_after_report(
        self,
        atm_id: int,
        issue_type: str,
    ) -> Optional[ATM]:
        """Decay reliability score based on report type."""
        decay_map = {
            "not_working": 0.10,
            "missing_service": 0.05,
            "out_of_cash": 0.08,
            "card_stuck": 0.12,
            "wrong_amount": 0.07,
        }
        decay = decay_map.get(issue_type, 0.02)

        atm = self.db.query(ATM).filter(ATM.id == atm_id).first()
        if not atm:
            return None

        # Read whichever reliability field exists
        current = getattr(atm, "reliability_score", None)
        if current is None:
            current = getattr(atm, "reliability", 1.0)
        current = float(current) if current is not None else 1.0

        new_score = max(0.0, min(1.0, current - decay))

        # Write to whichever field(s) exist
        if hasattr(atm, "reliability_score"):
            atm.reliability_score = new_score
        if hasattr(atm, "reliability"):
            atm.reliability = new_score

        # Auto-flag offline if reliability drops too low
        if new_score < 0.3 and hasattr(atm, "is_working"):
            atm.is_working = False

        self.db.commit()
        self.db.refresh(atm)

        if _CACHE_AVAILABLE:
            try:
                _cache_invalidate(CacheKeys.atm_detail(atm_id))
            except Exception:
                pass

        return atm


# ============================================================================
# Backward-compatible alias
# ============================================================================
AtmService = ATMService