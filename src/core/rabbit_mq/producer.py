import asyncio
import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import aio_pika
from aio_pika import DeliveryMode, ExchangeType, Message
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractQueue

from src.core.log.log import Log
from src.core.rabbit_mq.config import RabbitMQConfig


class AsyncRabbitMQProducer:
    def __init__(
        self,
        config: RabbitMQConfig,
        log: Log,
    ) -> None:
        self.config = config
        self.logger = log
        self._conn: AbstractConnection | None = None
        self._is_initialized = False

    async def initialize(self) -> None:
        if self._is_initialized:
            return

        try:
            self._conn = await aio_pika.connect_robust(
                url=self.config.url,
                heartbeat=self.config.heartbeat,
                connection_timeout=self.config.connection_timeout,
            )
            self._is_initialized = True
            self.logger.info("🚀 RabbitMQ producer initialized successfully")
        except Exception as e:
            self.logger.error(f"🛑 Failed to initialize RabbitMQ producer: {e}")
            raise

    async def close(self) -> None:
        if self._conn and not self._conn.is_closed:
            await self._conn.close()
            self._is_initialized = False
            self.logger.info("🚦 RabbitMQ producer closed")

    @property
    def is_connected(self) -> bool:
        return bool(self._is_initialized and self._conn and not self._conn.is_closed)

    @asynccontextmanager
    async def get_channel(self) -> AsyncGenerator[AbstractChannel]:
        if not self.is_connected:
            raise RuntimeError("🛑 Producer not initialized or connection lost")

        channel = await self._conn.channel()  # type: ignore
        try:
            yield channel
        finally:
            await channel.close()

    async def send_message(
        self,
        queue_name: str,
        message: dict[str, Any] | str | bytes,
        exchange_name: str,
        action: str | None = None,
        routing_key: str | None = None,
        priority: int = 0,
        expiration: int | None = None,
        headers: dict[str, Any] | None = None,
        durable: bool = True,
        content_type: str = "application/json",
    ) -> bool:
        try:
            async with self.get_channel() as channel:
                exchange = await channel.declare_exchange(
                    name=exchange_name,
                    type=ExchangeType.DIRECT,
                    durable=durable,
                    auto_delete=False,
                    internal=False,
                )

                queue = await channel.declare_queue(
                    name=queue_name,
                    durable=True,
                    exclusive=False,
                    auto_delete=False,
                )

                await queue.bind(exchange, routing_key=routing_key or queue_name)

                if isinstance(message, dict):
                    if action is not None:
                        message["action"] = action
                    body = json.dumps(message, ensure_ascii=False).encode("utf-8")
                elif isinstance(message, str):
                    body = message.encode("utf-8")
                else:
                    body = message

                msg = Message(
                    body,
                    delivery_mode=DeliveryMode.PERSISTENT if durable else DeliveryMode.NOT_PERSISTENT,
                    priority=priority,
                    content_type=content_type,
                    headers=headers or {},
                    expiration=expiration,
                    timestamp=datetime.now(),
                )

                await exchange.publish(msg, routing_key=routing_key or queue_name)

                self.logger.info(f"✉️ Message sent to queue '{queue_name}'")
                return True

        except Exception as e:
            self.logger.error(f"🛑 Failed to send message to {queue_name}: {e}")
            return False

    async def send_batch_messages(
        self, queue_name: str, messages: list[dict[str, Any] | str], **kwargs: Any
    ) -> dict[str, int]:
        results = {"success": 0, "failed": 0}

        tasks = [self.send_message(queue_name, message, **kwargs) for message in messages]

        results_list = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results_list:
            if isinstance(result, Exception):
                results["failed"] += 1
            elif result:
                results["success"] += 1
            else:
                results["failed"] += 1

        return results
