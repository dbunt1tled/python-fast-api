from dataclasses import dataclass


@dataclass
class RabbitMQConfig:
    host: str
    port: int
    username: str
    password: str
    virtual_host: str = "/"
    heartbeat: int = 600
    connection_timeout: int = 30
