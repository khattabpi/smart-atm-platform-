"""Event publisher — used by services after DB commit."""
import json
import aio_pika
from app.events.broker import EventBroker
from app.events.schemas import Event, EventType
from app.core.logging import get_logger

logger = get_logger(__name__)


async def publish(event_type: EventType, payload: dict) -> None:
    """
    Publish event after successful DB commit.
    Graceful: logs but never raises into request path.
    """
    exchange = EventBroker.exchange()
    if not exchange:
        logger.debug("broker.unavailable.skip_publish", event=event_type.value)
        return

    event = Event(event_type=event_type, payload=payload)
    message = aio_pika.Message(
        body=event.model_dump_json().encode(),
        content_type="application/json",
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        message_id=event.event_id,
        headers={"x-event-type": event_type.value, "x-version": event.version},
    )
    try:
        await exchange.publish(message, routing_key=event_type.value)
        logger.info("event.published", type=event_type.value, id=event.event_id)
    except Exception as e:
        logger.error("event.publish_failed", type=event_type.value, error=str(e))