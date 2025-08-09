import asyncio
import sys
from pathlib import Path


def setup_path() -> None:
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent.parent
    sys.path.insert(0, str(project_root))

async def main(loop: asyncio.AbstractEventLoop) -> int:
    setup_path()

    try:
        from src.cmd.worker.email.send_email import SendEmailHandler
        from src.core.di.container import Container
        from src.core.rabbit_mq.worker import RMWorker

        container = Container()
        log = container.log()
        worker = RMWorker(
            consumer=container.rmq_consumer(),
            queue="p_email",
            exchange="p_email_exchange",
            log=log
        )
        await worker.initialize(
            loop=loop,
            handlers=[SendEmailHandler(container=container)]
        )
        try:
            await worker.start()
        except Exception as e:
            log.error(f"🛑 Failed to start RabbitMQ worker: {e}")
        finally:
            await worker.stop()

        return 0

    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running this from the project root directory.")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main(loop))
    loop.close()
