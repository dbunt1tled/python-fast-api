import time
from dataclasses import dataclass
from typing import Any

from starlette.websockets import WebSocket


@dataclass
class IncomeMessage:
    uid: str
    user_id: str
    websocket: WebSocket
    data: dict[str, Any]
    timestamp: float

    def __post_init__(self) -> None:
        if not hasattr(self, "timestamp"):
            self.timestamp = time.time()
        if not hasattr(self, "message_id"):
            self.uid = f"{self.user_id}_{self.timestamp}_{id(self)}"
