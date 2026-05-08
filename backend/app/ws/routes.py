from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.ws.manager import manager
from app.ws.auth import authenticate_ws

router = APIRouter()


@router.websocket("/ws/atm-status")
async def ws_atm_status(ws: WebSocket):
    """Public global feed of ATM status changes."""
    await manager.connect("atm:status", ws)
    try:
        while True:
            # Keepalive — clients can send pings
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect("atm:status", ws)


@router.websocket("/ws/notifications")
async def ws_notifications(ws: WebSocket, token: str = Query(...)):
    """Authenticated per-user notification channel."""
    user_id = await authenticate_ws(ws, token)
    if user_id is None:
        return
    channel = f"user:{user_id}"
    await manager.connect(channel, ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(channel, ws)