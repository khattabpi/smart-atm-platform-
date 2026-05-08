"""RabbitMQ broker abstraction — swappable with Kafka later."""
from typing import Optional
import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel, AbstractExchange

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EventBroker:
    _connection: Optional[AbstractRobustConnection] = None
    _channel: Optional[AbstractRobustChannel] = None
    _exchange: Optional[AbstractExchange] = None
    _healthy: bool = False

    @classmethod
    async def init(cls) -> None:
        if not settings.RABBITMQ_ENABLED:
            logger.info("broker.disabled")
            return
        try:
            cls._connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            cls._channel = await cls._connection.channel()
            await cls._channel.set_qos(prefetch_count=20)

            # Dead Letter Exchange
            await cls._channel.declare_exchange(
                settings.EVENTS_DLX, aio_pika.ExchangeType.TOPIC, durable=True
            )
            cls._exchange = await cls._channel.declare_exchange(
                settings.EVENTS_EXCHANGE, aio_pika.ExchangeType.TOPIC, durable=True
            )
            cls._healthy = True
            logger.info("broker.connected")
        except Exception as e:
            cls._healthy = False
            logger.warning("broker.connection_failed", error=str(e))

    @classmethod
    async def close(cls) -> None:
        if cls._connection and not cls._connection.is_closed:
            await cls._connection.close()

    @classmethod
    def channel(cls) -> Optional[AbstractRobustChannel]:
        return cls._channel if cls._healthy else None

    @classmethod
    def exchange(cls) -> Optional[AbstractExchange]:
        return cls._exchange if cls._healthy else None

    @classmethod
    def is_healthy(cls) -> bool:
        return cls._healthy