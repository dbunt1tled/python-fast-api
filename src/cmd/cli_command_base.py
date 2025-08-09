import asyncio
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.di.container import Container
    from src.core.log.log import Log


class AsyncCLICommandBase(ABC):
    def __init__(self) -> None:
        self._container: Container | None = None
        self._log: Log | None = None

    @staticmethod
    def setup_path() -> None:
        script_dir = Path(__file__).parent.absolute()
        project_root = script_dir.parent.parent
        sys.path.insert(0, str(project_root))

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
            self.setup_path()
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
        try:
            exit_code = loop.run_until_complete(command.run(loop))
            sys.exit(exit_code)
        finally:
            loop.close()
