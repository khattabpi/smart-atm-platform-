from app.events.schemas import Event, UserRegisteredPayload
from app.core.logging import get_logger

logger = get_logger(__name__)


async def handle_user_registered(event: Event) -> None:
    payload = UserRegisteredPayload(**event.payload)
    # Future: send welcome email, init analytics, etc.
    logger.info("user.welcome.queued", user_id=payload.user_id, email=payload.email)