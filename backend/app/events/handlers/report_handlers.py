"""Handles report.submitted → reliability decay + cascading status event."""
from app.events.schemas import (
    Event,
    ReportSubmittedPayload,
    AtmStatusChangedPayload,
    EventType,
)
from app.events.publisher import publish
from app.database import SessionLocal
from app.models.atm import ATM
from app.core.logging import get_logger
from app.cache.decorators import invalidate, invalidate_pattern
from app.cache.keys import CacheKeys

logger = get_logger(__name__)

DECAY_MAP = {
    "not_working": 0.10,
    "missing_service": 0.05,
    "out_of_cash": 0.08,
    "card_stuck": 0.12,
    "wrong_amount": 0.07,
}


def _get_reliability(atm: ATM) -> float:
    """Read reliability from whichever field exists on the model."""
    val = getattr(atm, "reliability_score", None)
    if val is None:
        val = getattr(atm, "reliability", 1.0)
    return float(val if val is not None else 1.0)


def _set_reliability(atm: ATM, value: float) -> None:
    """Write reliability to whichever field(s) exist on the model."""
    if hasattr(atm, "reliability_score"):
        atm.reliability_score = value
    if hasattr(atm, "reliability"):
        atm.reliability = value


async def handle_report_submitted(event: Event) -> None:
    """
    Process a report.submitted event:
      1. Decay the ATM's reliability score
      2. Auto-flag as not working if reliability < 0.3
      3. Invalidate caches
      4. Cascade an atm.status_changed event if status flipped
    """
    payload = ReportSubmittedPayload(**event.payload)
    decay = DECAY_MAP.get(payload.issue_type, 0.02)

    db = SessionLocal()
    try:
        atm = db.query(ATM).filter(ATM.id == payload.atm_id).first()
        if not atm:
            logger.warning("event.atm_not_found", atm_id=payload.atm_id)
            return

        old_working = bool(getattr(atm, "is_working", True))
        old_reliability = _get_reliability(atm)
        new_reliability = max(0.0, min(1.0, old_reliability - decay))

        _set_reliability(atm, new_reliability)

        # Auto-flag offline if reliability drops too low
        if new_reliability < 0.3 and hasattr(atm, "is_working"):
            atm.is_working = False

        db.commit()
        db.refresh(atm)

        logger.info(
            "report.processed",
            atm_id=atm.id,
            old_reliability=round(old_reliability, 3),
            new_reliability=round(new_reliability, 3),
            now_working=bool(getattr(atm, "is_working", True)),
        )

        # Invalidate caches (best-effort — graceful if Redis is down)
        try:
            await invalidate(CacheKeys.atm_detail(atm.id))
            await invalidate_pattern(CacheKeys.ATMS_NEARBY_PATTERN)
        except Exception as e:
            logger.warning("cache.invalidate_failed_in_handler", error=str(e))

        # Cascade event if working-status changed
        if old_working != bool(getattr(atm, "is_working", True)):
            await publish(
                EventType.ATM_STATUS_CHANGED,
                AtmStatusChangedPayload(
                    atm_id=atm.id,
                    is_working=bool(atm.is_working),
                    reliability=new_reliability,
                ).model_dump(),
            )
            logger.info("event.cascaded.atm_status_changed", atm_id=atm.id)
    finally:
        db.close()