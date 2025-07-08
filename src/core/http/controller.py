from abc import ABC

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter

from src.core.di.container import Container


class BaseController(ABC):
    def __init__(self, prefix: str = "", tags: list | None = None):
        self.router = APIRouter(prefix=prefix, tags=tags or [])
        self._container: Container | None = None

    @property
    def container(self):
        if self._container is None:
            raise RuntimeError("Container not initialized. Call setup_dependencies first.")
        return self._container

    @inject
    def setup_dependencies(self, container: Container = Provide[Container]):
        self._container = container
        return self

    def init(self) -> None:
        pass