from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class ProcessingResult(Enum):
    SUCCESS = "success"
    RETRY = "retry"
    REJECT = "reject"


@dataclass
class MessageContext:
    action: str
    payload: dict[str, Any]
    headers: dict[str, Any]
    routing_key: str
    queue_name: str
    delivery_tag: int
    redelivered: bool
    timestamp: datetime | None = None

    def to_str(self) -> str:
        return f"Action: {self.action}, Payload: {self.payload}"
