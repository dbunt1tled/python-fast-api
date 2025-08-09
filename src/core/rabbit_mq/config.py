from dataclasses import dataclass


@dataclass
class RabbitMQConfig:
    url: str
    heartbeat: int = 600
    connection_timeout: int = 30
