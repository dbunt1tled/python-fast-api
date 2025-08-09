import asyncio
import json
import time
import traceback

import aio_pika
from aio_pika import ExchangeType
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractIncomingMessage

from src.core.log.log import Log
from src.core.rabbit_mq.config import RabbitMQConfig
from src.core.rabbit_mq.data import MessageContext, ProcessingResult
from src.core.rabbit_mq.message_handler import MessageHandler
from src.core.service.statistics import render_statistics


class AsyncRabbitMQConsumer:
    def __init__(self, config: RabbitMQConfig, log: Log) -> None:
        self.config = config
        self.logger = log
        self._conn: AbstractConnection | None = None
        self._channel: dict[str, AbstractChannel] = {}
        self._handlers: dict[str, MessageHandler] = {}
        self._is_initialized = False
        self._running = False
        self._shutdown_event = asyncio.Event()

    async def initialize(
        self,
        loop: asyncio.AbstractEventLoop,
    ) -> None:
        if self._is_initialized:
            return

        try:
            self._conn = await aio_pika.connect_robust(
                url=self.config.url,
                heartbeat=self.config.heartbeat,
                connection_timeout=self.config.connection_timeout,
                loop=loop,
            )
            self._is_initialized = True
            self.logger.info("🚀 RabbitMQ consumer initialized successfully")
        except Exception as e:
            self.logger.error(f"🛑 Failed to initialize RabbitMQ consumer: {e}")
            raise

    async def close(self) -> None:
        self._running = False
        self._shutdown_event.set()

        for channel in self._channel.values():
            if not channel.is_closed:
                await channel.close()

        if self._conn and not self._conn.is_closed:
            await self._conn.close()

        self._is_initialized = False
        self._channel.clear()
        self.logger.info("🚦 RabbitMQ consumer closed")

    def register_handler(self, handler: MessageHandler) -> None:
        handler_name = handler.__class__.__name__
        self._handlers[handler_name] = handler
        self.logger.info(f"📨 RabbitMQ consumer registered handler: {handler_name}")

    def get_handler(self, action: str) -> MessageHandler | None:
        for handler in self._handlers.values():
            if handler.can_handle(action):
                return handler
        return None

    async def _create_channel(self, queue_name: str) -> AbstractChannel:
        if not self._conn:
            raise RuntimeError("🛑 Connection to RabbitMQ is not established")

        channel = await self._conn.channel()  # type: ignore
        await channel.set_qos(prefetch_count=1)
        self._channel[queue_name] = channel
        return channel

    async def _parse_message(self, message: AbstractIncomingMessage, queue_name: str) -> MessageContext:
        try:
            body = message.body.decode("utf-8")
            payload = json.loads(body)
            action = payload.get("action")
            if not action:
                raise ValueError("🛑 Action not found in message")

            return MessageContext(
                action=action,
                payload=payload,
                headers=dict(message.headers) if message.headers else {},
                routing_key=message.routing_key or "",
                queue_name=queue_name,
                delivery_tag=message.delivery_tag or 0,
                redelivered=message.redelivered or False,
                timestamp=message.timestamp or None,
            )
        except Exception as e:
            self.logger.error(f"🛑 Failed to parse message: {e}")
            raise

    async def _process_message(self, message: AbstractIncomingMessage, queue_name: str) -> None:
        start_time = time.time()
        context: MessageContext | None = None
        try:
            context = await self._parse_message(message=message, queue_name=queue_name)
            handler = self.get_handler(context.action)
            if not handler:
                self.logger.info(f"☄️🐇 Consumer skipped message: {context.to_str()}")
                await message.reject(requeue=False)
                return

            self.logger.info(f"🪢🐇 Consumer start process message: {context.to_str()}")
            result = await handler.handle(context)
            if result == ProcessingResult.SUCCESS:
                await message.ack()
                self.logger.info(
                    f"🧩🐇 Consumer processed message successfully: {context.to_str()}, {render_statistics(start_time=start_time)}"
                )
            elif result == ProcessingResult.RETRY:
                self.logger.info(
                    f"♻️🐇 Consumer message requeued for retry: {context.to_str()}, {render_statistics(start_time=start_time)}"
                )
                await message.reject(requeue=True)
            else:
                self.logger.info(
                    f"🚫🐇 Consumer message rejected: {context.to_str()}, {render_statistics(start_time=start_time)}"
                )
                await message.reject(requeue=False)
        except Exception as e:
            self.logger.error(
                f"🛑🐇 Failed to process message: {e},  {context.to_str() if context is not None else ''} {render_statistics(start_time=start_time)}",
                error=traceback.extract_tb(e.__traceback__)[-1],
            )
            await message.reject(requeue=False)

    async def consume(
        self,
        queue_name: str,
        exchange_name: str,
        durable: bool = True,
        exclusive: bool = False,
        auto_delete: bool = False,
    ) -> None:
        if not self._is_initialized or not self._conn:
            raise RuntimeError("🛑 RabbitMQ consumer is not initialized")
        try:
            async with self._conn:
                channel = await self._conn.channel()  # type: ignore
                await channel.set_qos(prefetch_count=1)

                exchange = await channel.declare_exchange(
                    name=exchange_name,
                    type=ExchangeType.DIRECT,
                    durable=durable,
                    auto_delete=auto_delete,
                    internal=False,
                )

                queue = await channel.declare_queue(
                    queue_name,
                    durable=durable,
                    exclusive=exclusive,
                    auto_delete=auto_delete,
                )

                await queue.bind(exchange, queue_name)

                await queue.consume(lambda message: self._process_message(message, queue_name), no_ack=False)

                self._running = True
                self.logger.info(f"🚀 RabbitMQ consumer started consuming messages from queue: {queue_name}")
                await self._shutdown_event.wait()
        except Exception as e:
            self.logger.error(
                f"🛑 Failed to consume messages from queue {queue_name}: {e}",
                error=traceback.extract_tb(e.__traceback__)[-1],
            )
            raise
