"""
Worker entrypoint — runs independently from the API.
Start with:  python -m app.workers.main
"""
import asyncio
import signal

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.cache.redis_client import RedisClient
from app.events.broker import EventBroker
from app.events.consumer import EventConsumer
from app.events.schemas import EventType

# Handlers
from app.events.handlers.report_handlers import handle_report_submitted
from app.events.handlers.atm_handlers import handle_atm_status_changed
from app.events.handlers.transaction_handlers import handle_transaction_completed
from app.events.handlers.user_handlers import handle_user_registered

configure_logging(settings.ENV)
logger = get_logger(__name__)


async def run_worker():
    await RedisClient.init()
    await EventBroker.init()

    consumer = EventConsumer()
    consumer.register(EventType.REPORT_SUBMITTED, handle_report_submitted)
    consumer.register(EventType.ATM_STATUS_CHANGED, handle_atm_status_changed)
    consumer.register(EventType.TRANSACTION_COMPLETED, handle_transaction_completed)
    consumer.register(EventType.USER_REGISTERED, handle_user_registered)

    await consumer.start(
        queue_name="smart_atm.workers.main",
        routing_keys=[
            EventType.REPORT_SUBMITTED.value,
            EventType.ATM_STATUS_CHANGED.value,
            EventType.TRANSACTION_COMPLETED.value,
            EventType.USER_REGISTERED.value,
        ],
    )

    logger.info("worker.running")

    # Keep process alive until signal
    stop = asyncio.Event()

    def _on_signal():
        logger.info("worker.signal_received")
        stop.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _on_signal)
        except NotImplementedError:
            pass  # Windows

    await stop.wait()
    await EventBroker.close()
    await RedisClient.close()
    logger.info("worker.stopped")


if __name__ == "__main__":
    asyncio.run(run_worker())