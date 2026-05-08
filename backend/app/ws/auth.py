from fastapi import WebSocket, status
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedError


async def authenticate_ws(ws: WebSocket, token: str | None) -> int | None:
    if not token:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return None
    try:
        payload = decode_token(token)
        return int(payload["sub"])
    except (UnauthorizedError, KeyError, ValueError):
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return None