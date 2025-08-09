import asyncio

from src.cmd.worker.email.handler.send_email import SendEmailHandler
from src.core.di.container import Container
from src.core.rabbit_mq.worker import RMWorker


async def main() -> None:
    container = Container()
    logger = container.log()
    worker = RMWorker(
        consumer=container.rmq_consumer(),
        queues=["email"],
        log=logger
    )
    await worker.initialize(
        handlers=[SendEmailHandler(container=container, logger=logger)]
    )
    try:
        await worker.start()
    except Exception as e:
        logger.error(f"🛑 Failed to start RabbitMQ worker: {e}")
    finally:
        await worker.stop()

if __name__ == "__main__":
    asyncio.run(main())
