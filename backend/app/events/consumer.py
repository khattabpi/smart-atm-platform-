"""Generic event consumer with retry + DLQ."""
import json
import asyncio
from typing import Callable, Awaitable
import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from app.events.broker import EventBroker
from app.events.schemas import Event, EventType
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

EventHandler = Callable[[Event], Awaitable[None]]
MAX_RETRIES = 3


class EventConsumer:
    def __init__(self):
        self._handlers: dict[EventType, list[EventHandler]] = {}

    def register(self, event_type: EventType, handler: EventHandler) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    async def start(self, queue_name: str, routing_keys: list[str]) -> None:
        channel = EventBroker.channel()
        exchange = EventBroker.exchange()
        if not channel or not exchange:
            logger.warning("consumer.broker_unavailable")
            return

        # DLQ
        dlq = await channel.declare_queue(
            f"{queue_name}.dlq",
            durable=True,
            arguments={"x-message-ttl": 1000 * 60 * 60 * 24},
        )
        await dlq.bind(settings.EVENTS_DLX, routing_key="#")

        # Main queue with DLX
        queue = await channel.declare_queue(
            queue_name,
            durable=True,
            arguments={
                "x-dead-letter-exchange": settings.EVENTS_DLX,
                "x-dead-letter-routing-key": queue_name,
            },
        )
        for rk in routing_keys:
            await queue.bind(exchange, routing_key=rk)

        await queue.consume(self._on_message)
        logger.info("consumer.started", queue=queue_name, keys=routing_keys)

    async def _on_message(self, message: AbstractIncomingMessage) -> None:
        retries = int(message.headers.get("x-retries", 0)) if message.headers else 0
        try:
            data = json.loads(message.body.decode())
            event = Event(**data)

            # Idempotency: optional dedupe via Redis SETNX on event_id
            handlers = self._handlers.get(event.event_type, [])
            for handler in handlers:
                await handler(event)

            await message.ack()
            logger.info("event.handled", type=event.event_type.value, id=event.event_id)
        except Exception as e:
            logger.error("event.handler_failed", error=str(e), retries=retries)
            if retries >= MAX_RETRIES:
                await message.reject(requeue=False)  # Goes to DLQ
            else:
                # Exponential backoff before requeue
                await asyncio.sleep(2 ** retries)
                # Republish with incremented retry counter
                await self._republish_with_retry(message, retries + 1)
                await message.ack()

    async def _republish_with_retry(self, message: AbstractIncomingMessage, retries: int) -> None:
        exchange = EventBroker.exchange()
        if not exchange:
            return
        new_msg = aio_pika.Message(
            body=message.body,
            headers={**(message.headers or {}), "x-retries": retries},
            content_type=message.content_type,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        await exchange.publish(new_msg, routing_key=message.routing_key)