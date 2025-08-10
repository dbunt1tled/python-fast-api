from typing import Any

from fastapi import WebSocket

from src.core.web_socket.enum.ws_type import WSType


class WSHandler:
    async def add_connection(self, user_id: str, websocket: WebSocket) -> None:
        raise NotImplementedError

    async def remove_connection(self, user_id: str, websocket: WebSocket) -> None:
        raise NotImplementedError

    async def process_message(self, user_id: str,message: dict[str, Any], websocket: WebSocket) -> None:
        raise NotImplementedError

    @staticmethod
    def can(ws_type: WSType) -> bool:
        raise NotImplementedError