from dataclasses import dataclass
from typing import Any

from aio_pika import ExchangeType


@dataclass
class RabbitMQConfig:
    url: str
    heartbeat: int = 600
    connection_timeout: int = 30


@dataclass
class ExchangeConfig:
    name: str
    type: ExchangeType = ExchangeType.DIRECT
    durable: bool = True
    auto_delete: bool = False
    internal: bool = False
    arguments: dict[str, Any] | None = None


@dataclass
class QueueConfig:
    name: str
    durable: bool = True
    exclusive: bool = False
    auto_delete: bool = False
    arguments: dict[str, Any] | None = None
