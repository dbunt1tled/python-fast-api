import logging
from abc import ABC
from typing import Any

from src.core.di.container import Container
from src.core.http.response.api_response_service import ApiResponseService
from src.core.http.response.response import JsonApiResponse
from src.core.log.log import Log
from src.core.settings.setting import Settings


class BaseController(ABC):
    def __init__(self, container: Container):
        self.container = container
        self.api_response_service = ApiResponseService(container=container)
        self.logger = logging.getLogger(__name__)

    def get_container(self) -> Container:
        return self.container

    def get_api_config(self) -> Settings:
        return self.container.app_config()

    def log(self) -> Log:
        return self.container.log()

    async def response(
        self,
        data: Any | None = None,
        meta: dict[str, Any] | None = None,
        resource_type: str | None = None,
        include: str | None = None,
    ) -> JsonApiResponse:
        return await self.api_response_service.response(
            data=data, meta=meta, resource_type=resource_type, include=include
        )
