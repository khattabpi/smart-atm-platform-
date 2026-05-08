"""Handles atm.status_changed → broadcasts to WebSocket via Redis Pub/Sub."""
import json
from app.events.schemas import Event, AtmStatusChangedPayload
from app.cache.redis_client import get_redis
from app.core.logging import get_logger

logger = get_logger(__name__)

WS_CHANNEL_ATM_STATUS = "ws:atm:status"


async def handle_atm_status_changed(event: Event) -> None:
    payload = AtmStatusChangedPayload(**event.payload)
    r = get_redis()
    if not r:
        return
    try:
        await r.publish(WS_CHANNEL_ATM_STATUS, json.dumps({
            "atm_id": payload.atm_id,
            "is_working": payload.is_working,
            "reliability": payload.reliability,
        }))
        logger.info("ws.broadcast.atm_status", atm_id=payload.atm_id)
    except Exception as e:
        logger.error("ws.broadcast_failed", error=str(e))