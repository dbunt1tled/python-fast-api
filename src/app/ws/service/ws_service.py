import json
from typing import Any

from fastapi import WebSocket, status

from src.app.ws.service.ws_handler import WSHandler
from src.core.log.log import Log
from src.core.service.functions import is_enum_value
from src.core.service.hash_service import HashService
from src.core.web_socket.enum.ws_type import WSType
from src.core.web_socket.ws_manager import WSManager


class WSService(WSHandler):
    def __init__(
        self,
        ws_manager: WSManager,
        hash_service: HashService,
        services: list[WSHandler],
        log: Log,
    ) -> None:
        self.ws_manager = ws_manager
        self.hash_service = hash_service
        self.log = log
        self.services = services

    async def add_connection(self, user_id: str, websocket: WebSocket) -> None:
        token = websocket.query_params.get("token")
        if token is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            self.log.error(f"WS connect: user {user_id}, no token provided")
            return
        try:
            user = self.hash_service.verify_token(token)
            if user is None or user.subject != user_id:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                self.log.error(f"WS connect: user {user_id}, invalid token")
                return
        except Exception as e:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            self.log.error(f"WS connect: user {user_id}, invalid token: {e}")
            return

        await self.ws_manager.connect(user_id, websocket)
        for service in self.services:
            await service.add_connection(user_id, websocket)

    async def process_message(self, user_id: str, message: dict[str, Any], websocket: WebSocket) -> None:
        tp = message.get("type", WSType.UNKNOWN.value)
        if not is_enum_value(enum_class=WSType, value=tp):
            self.log.warning(f"WS message: user {user_id}, unknown message type: {message}")
            return
        message_type = WSType(tp)
        if message_type == WSType.PING:
            await websocket.send_text(json.dumps({"type": "pong"}))
            return

        if message_type == WSType.MESSAGE_READ:
            message_type = WSType(message.get("type_read", WSType.UNKNOWN.value))

        if message_type == WSType.UNKNOWN:
            self.log.warning(f"WS message: user {user_id}, unknown message type: {message}")
            return

        for service in self.services:
            if service.can(ws_type=message_type):
                await service.process_message(user_id=user_id, message=message, websocket=websocket)
                return
        self.log.error(f"WS message: user {user_id}, {message_type} message type without handler: {message}")

    async def remove_connection(self, user_id: str, websocket: WebSocket) -> None:
        for service in self.services:
            await service.remove_connection(user_id=user_id, websocket=websocket)
        await self.ws_manager.disconnect(user_id=user_id, websocket=websocket)

    @staticmethod
    def can(ws_type: WSType) -> bool:
        return True
