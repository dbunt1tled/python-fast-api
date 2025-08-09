import asyncio
import signal
import sys
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.core.di.container import Container
    from src.core.log.log import Log


class AsyncCLICommandBase(ABC):
    def __init__(self) -> None:
        self._container: Container | None = None
        self._log: Log | None = None

    def initialize_container(self) -> None:
        from src.core.di.container import Container

        self._container = Container()
        self._log = self._container.log()

    @property
    def container(self) -> "Container":
        if self._container is None:
            raise RuntimeError("Container not initialized. Call initialize_container() first.")
        return self._container

    @property
    def log(self) -> "Log":
        if self._log is None:
            raise RuntimeError("Logger not initialized. Call initialize_container() first.")
        return self._log

    @abstractmethod
    async def execute(self, loop: asyncio.AbstractEventLoop) -> int:
        pass

    async def run(self, loop: asyncio.AbstractEventLoop) -> int:
        try:
            self.initialize_container()
            return await self.execute(loop)
        except ImportError as e:
            print(f"Import error: {e}")
            print("Make sure you're running this from the project root directory.")
            return 1
        except Exception as e:
            if self._log:
                self._log.error(f"CLI command failed: {e}", error=e.__dict__)
            else:
                print(f"Error: {e}, type: {type(e)}, traceback: {e.__traceback__}")
            return 1

    @classmethod
    def start(cls) -> None:
        command = cls()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        shutdown_event = asyncio.Event()
        main_task = None

        def signal_handler(signum: int, frame: Any) -> None:
            print(f"\n🛑 Received signal {signum}. Initiating graceful shutdown...")
            if main_task and not main_task.done():
                main_task.cancel()
            shutdown_event.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            main_task = loop.create_task(command.run(loop))
            exit_code = loop.run_until_complete(main_task)
            sys.exit(exit_code)
        except asyncio.CancelledError:
            print("🚦 Command was cancelled gracefully")
            sys.exit(0)
        except KeyboardInterrupt:
            print("🚦 Keyboard interrupt received, shutting down...")
            sys.exit(0)
        finally:
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()

            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

            loop.close()
