import json
from app.events.schemas import Event, TransactionCompletedPayload
from app.cache.redis_client import get_redis


async def handle_transaction_completed(event: Event) -> None:
    payload = TransactionCompletedPayload(**event.payload)
    r = get_redis()
    if not r:
        return
    await r.publish(
        f"ws:user:{payload.user_id}:notifications",
        json.dumps({
            "type": "transaction_completed",
            "transaction_id": payload.transaction_id,
            "amount": payload.amount,
            "tx_type": payload.type,
        }),
    )