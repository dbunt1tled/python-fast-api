from abc import ABC

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter

from src.core.di.container import Container
from src.core.http.response.api_response_service import ApiResponseService


class BaseController(ABC):
    def __init__(self, prefix: str = "", tags: list | None = None):
        self.router = APIRouter(prefix=prefix, tags=tags or [])
        self._container: Container | None = None
        self._api_response: ApiResponseService | None = None

    @property
    def container(self) -> Container:
        if self._container is None:
            raise RuntimeError("Container not initialized. Call setup_dependencies first.")
        return self._container

    @property
    def api_response(self) -> ApiResponseService:
        if self._api_response is None:
            raise RuntimeError("Container not initialized. Call setup_dependencies first.")
        return self._api_response

    @inject
    def setup_dependencies(self, container: Container = Provide[Container]) -> "BaseController":
        self._container = container
        self._api_response = ApiResponseService(container)
        return self

    def init(self) -> None:
        pass