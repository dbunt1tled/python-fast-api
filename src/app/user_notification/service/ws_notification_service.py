from datetime import datetime
from typing import Any

from fastapi import WebSocket

from src.app.user_notification.data.user_notification_status import UserNotificationStatus
from src.app.user_notification.service.user_notification_service import UserNotificationService
from src.app.ws.service.ws_handler import WSHandler
from src.core.log.log import Log
from src.core.web_socket.enum.ws_type import WSType
from src.core.web_socket.ws_manager import WSManager


class WSNotificationService(WSHandler):
    def __init__(
            self,
            user_notification_service: UserNotificationService,
            ws_manager: WSManager,
            log: Log,
    ) -> None:
        self.user_notification_service = user_notification_service
        self.ws_manager = ws_manager
        self.log = log

    async def add_connection(self, user_id: str, websocket: WebSocket) -> None:
        notifications = await self.user_notification_service.new_by_user_id(uid=int(user_id))
        for notification in notifications:
            await self.ws_manager.send_to_user(
                user_id=user_id,
                data={
                    "type": WSType.USER_NOTIFICATION.value,
                    "data": {
                        "message": notification.data.get("message"),
                        "status": notification.status.value,
                        "createdAt": notification.created_at.isoformat() if isinstance(notification.created_at, datetime) else str(notification.created_at),
                    }
                },
                websocket=websocket,
            )
        self.log.info(f"WS connect: user {user_id}, {len(notifications)} notifications sent")

    async def process_message(self, user_id: str,message: dict[str, Any], websocket: WebSocket) -> None:
        message_type = WSType(message.get("type", WSType.UNKNOWN.value))
        if message_type == WSType.USER_NOTIFICATION:
            await self.user_notification_service.create(
                data={
                    "user_id": int(user_id),
                    "message": message.get("message"),
                    "status": UserNotificationStatus.NEW,
                },
            )
            return
        if message_type == WSType.MESSAGE_READ:
            uid = message.get("id")
            if uid is None:
                self.log.warning(f"WS message: user {user_id}, message_read message without id: {message}")
                return
            notification = await self.user_notification_service.update(
                uid=int(uid),
                data={
                    "status": UserNotificationStatus.READ,
                },
            )
            await self.ws_manager.send_to_user(
                user_id=user_id,
                data={
                    "type": WSType.USER_NOTIFICATION.value,
                    "data": {
                        "message": notification.data.get("message"),
                        "status": notification.status.value,
                        "createdAt": notification.created_at.isoformat() if isinstance(notification.created_at, datetime) else str(notification.created_at),
                    }
                },
            )
            return


    async def remove_connection(self, user_id: str, websocket: WebSocket) -> None:
        pass

    @staticmethod
    def can(ws_type: WSType) -> bool:
        return ws_type == WSType.USER_NOTIFICATION
