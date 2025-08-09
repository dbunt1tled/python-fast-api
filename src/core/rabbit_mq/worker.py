import asyncio

from src.core.log.log import Log
from src.core.rabbit_mq.consumer import AsyncRabbitMQConsumer
from src.core.rabbit_mq.hadler import MessageHandler


class RMWorker:
    def __init__(
            self,
            consumer: AsyncRabbitMQConsumer,
            queues: list[str],
            log: Log
    ) -> None:
        self.consumer = consumer
        self.queues = queues
        self.logger = log
        self._tasks: list[asyncio.Task] = []

    async def initialize(self, handlers: list[MessageHandler]) -> None:
        await self.consumer.initialize()
        for handler in handlers:
            self.consumer.register_handler(handler)
        self.logger.info("🚀 RabbitMQ worker initialized successfully")

    async def start(self) -> None:
        try:
            for queue in self.queues:
                task = asyncio.create_task(self.consumer.consume(queue_name=queue))
                self._tasks.append(task)
            self.logger.info(f"🧨 RabbitMQ worker started successfully, consuming messages from {len(self.queues)} queues")
            await asyncio.gather(*self._tasks)
        except Exception as e:
            self.logger.error(f"🛑 Failed to start RabbitMQ worker: {e}")
            await self.stop()
            raise


    async def stop(self) -> None:
        for task in self._tasks:
            if not task.done():
                task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self.logger.info("🚦 RabbitMQ worker stopped successfully")
