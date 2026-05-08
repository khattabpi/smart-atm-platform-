"""Connection manager — tracks active WebSockets per channel."""
from collections import defaultdict
from typing import Set
from fastapi import WebSocket
from app.core.logging import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    def __init__(self):
        self._channels: dict[str, Set[WebSocket]] = defaultdict(set)

    async def connect(self, channel: str, ws: WebSocket) -> None:
        await ws.accept()
        self._channels[channel].add(ws)
        logger.info("ws.connected", channel=channel, total=len(self._channels[channel]))

    def disconnect(self, channel: str, ws: WebSocket) -> None:
        self._channels[channel].discard(ws)

    async def broadcast(self, channel: str, message: str) -> None:
        dead: list[WebSocket] = []
        for ws in self._channels.get(channel, set()):
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._channels[channel].discard(ws)


manager = ConnectionManager()