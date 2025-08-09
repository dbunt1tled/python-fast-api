import asyncio
import sys
from pathlib import Path


def setup_path() -> None:
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent.parent
    sys.path.insert(0, str(project_root))


setup_path()

from src.cmd.cli_command_base import AsyncCLICommandBase  # noqa: E402


class EmailWorker(AsyncCLICommandBase):
    async def execute(self, loop: asyncio.AbstractEventLoop) -> int:
        try:
            from src.cmd.worker.email.send_email import SendEmailHandler
            from src.core.rabbit_mq.worker import RMWorker

            worker = RMWorker(
                consumer=self.container.rmq_consumer(), queue="p_email", exchange="p_email_exchange", log=self.log
            )

            await worker.initialize(loop=loop, handlers=[SendEmailHandler(container=self.container)])

            try:
                self.log.info("🚀 Starting email worker...")
                await worker.start()
            except asyncio.CancelledError:
                self.log.info("🚦 Email worker cancelled, shutting down gracefully...")
                return 0
            except Exception as e:
                self.log.error(f"🛑 Failed to start RabbitMQ worker: {e}")
                return 1
            finally:
                await worker.stop()
                self.log.info("🛑 Email worker stopped")

            return 0

        except Exception as e:
            self.log.error(f"Email worker execution failed: {e}")
            return 1


if __name__ == "__main__":
    EmailWorker.start()
