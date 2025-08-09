import asyncio

from src.core.log.log import Log
from src.core.rabbit_mq.consumer import AsyncRabbitMQConsumer
from src.core.rabbit_mq.message_handler import MessageHandler


class RMWorker:
    def __init__(self, consumer: AsyncRabbitMQConsumer, queue: str, exchange: str, log: Log) -> None:
        self.consumer = consumer
        self.queue = queue
        self.exchange = exchange
        self.logger = log

    async def initialize(self, loop: asyncio.AbstractEventLoop, handlers: list[MessageHandler]) -> None:
        await self.consumer.initialize(loop=loop)
        for handler in handlers:
            self.consumer.register_handler(handler)
        self.logger.info("🚀 RabbitMQ worker initialized successfully")

    async def start(self) -> None:
        try:
            await self.consumer.consume(
                queue_name=self.queue, exchange_name=self.exchange, durable=True, exclusive=False, auto_delete=False
            )
        except Exception as e:
            self.logger.error(f"🛑 Failed to start RabbitMQ worker: {e}")
            await self.stop()
            raise

    async def stop(self) -> None:
        await self.consumer.close()
        self.logger.info("🚦 RabbitMQ worker stopped successfully")
