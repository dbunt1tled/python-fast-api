from collections.abc import Sequence
from typing import Any

from pydantic_core import ErrorDetails

from src.app.user.dto.user import UserResponse
from src.app.user_notification.dto.user_notification import UserNotificationResponse
from src.core.db.repository import Paginator
from src.core.di.container import Container
from src.core.http.response.response import ResponseBaseModel, JsonApiError, JsonApiResource, JsonApiResponse


class ApiResponseService:
    def __init__(self, container: Container):
        self.container = container
        self._model_responses: dict[str, ResponseBaseModel] = {}
        self._register_model_responses()

    def _register_model_responses(self) -> None:
        self._model_responses = {
            "User": UserResponse(self.container),
            "UserNotification": UserNotificationResponse(self.container),
        }

    def register_model_response(self, model_name: str, response_class: type[ResponseBaseModel]) -> None:
        self._model_responses[model_name] = response_class(self.container)

    def get_model_response(self, model_name: str) -> ResponseBaseModel | None:
        return self._model_responses.get(model_name)

    async def response(
            self,
            data: Any | None = None,
            errors: list[JsonApiError | dict[str, Any]] | None = None,
            meta: dict[str, Any] | None = None,
            resource_type: str | None = None,
            include: str | None = None
    ) -> JsonApiResponse:
        if data is None and errors is None:
            return JsonApiResponse(meta=meta)

        if errors:
            return JsonApiResponse(
                errors=[error.model_dump() if hasattr(error, "model_dump") else error for error in errors],
                meta=meta,
            )

        if resource_type is None:
            if isinstance(data, Paginator):
                resource_type = data.items[0].__class__.__name__ if data.items else data.__class__.__name__
            elif isinstance(data, list) and data:
                resource_type = data[0].__class__.__name__
            else:
                resource_type = data.__class__.__name__

        model_response = self.get_model_response(resource_type)
        include_params: dict[str, bool] | None = None
        if model_response:
            if include is not None:
                include_params = {inc.strip(): True for inc in include.split(",")}
            return await self._response_with_model_handler(data, model_response, meta, include_params)
        else:
            return self._response_without_model_handler(data, resource_type, meta)

    async def _response_with_model_handler(
            self,
            data: Any,
            model_response: ResponseBaseModel,
            meta: dict[str, Any] | None = None,
            include_params: dict[str, bool] | None = None
    ) -> JsonApiResponse:
        resources: list[JsonApiResource] | list[dict[str, Any]] | JsonApiResource = []  # noqa
        included_resources: list[JsonApiResource] | list[dict[str, Any]] = [] # noqa

        if isinstance(data, Paginator):
            resources = await self._map_items_with_model_response(data.items, model_response, include_params)
            included_resources = await self._process_includes_for_list(data.items, model_response, include_params)
            meta = {
                "total": data.total,
                "page": data.page,
                "perPage": data.per_page,
                "totalPages": data.pages,
                **(meta or {})
            }
        elif isinstance(data, list):
            resources = await self._map_items_with_model_response(data, model_response, include_params)
            included_resources = await self._process_includes_for_list(data, model_response, include_params)
        else:
            resources = await self._data_to_resource_with_model_response(data, model_response, include_params)
            included_resources = await self._process_includes_for_item(data, model_response, include_params)

        response_data = {
            "data": resources,
            "meta": meta
        }

        if included_resources:
            response_data["included"] = included_resources

        return JsonApiResponse(
            data=resources,
            included=included_resources if included_resources else None,
            meta=meta
        )

    def _response_without_model_handler(self, data: Any, resource_type: str, meta: dict[str, Any] | None = None) -> JsonApiResponse:
        resources: list[JsonApiResource] | list[dict[str, Any]] | JsonApiResource = []  # noqa

        if isinstance(data, Paginator):
            resources = self.map_items(data.items)
            meta = {
                "total": data.total,
                "page": data.page,
                "perPage": data.per_page,
                "totalPages": data.pages,
                **(meta or {})
            }
        elif isinstance(data, list):
            resources = self.map_items(data)
        else:
            resources = ResponseBaseModel.data_to_resource(data, resource_type)

        return JsonApiResponse(data=resources, meta=meta)

    @staticmethod
    async def _map_items_with_model_response(
            data: list[Any] | Sequence[Any],
            model_response: ResponseBaseModel,
            include_params: dict[str, bool] | None = None
    ) -> list[JsonApiResource]:
        if not data:
            return []

        resources = []
        included = await model_response.process_includes(data, include_params or {})

        for item in data:
            resource = ResponseBaseModel.data_to_resource(item, model_response.get_resource_type())
            resource = model_response.add_relationships_to_resource(resource, item, included)
            resources.append(resource)

        return resources

    @staticmethod
    async def _data_to_resource_with_model_response(
            data: Any,
            model_response: ResponseBaseModel,
            include_params: dict[str, bool] | None = None
    ) -> JsonApiResource:
        included = await model_response.process_includes(data, include_params or {})
        resource = model_response.data_to_resource(data, model_response.get_resource_type())
        resource = model_response.add_relationships_to_resource(resource, data, included)
        return resource

    @staticmethod
    async def _process_includes_for_list(
            data: list[Any] | Sequence[Any],
            model_response: ResponseBaseModel,
            include_params: dict[str, bool] | None = None
    ) -> list[JsonApiResource]:
        if not include_params:
            return []

        included = await model_response.process_includes(data, include_params)
        all_included = []

        for resources in included.values():
            all_included.extend(resources)

        return all_included

    @staticmethod
    async def _process_includes_for_item(
            data: Any,
            model_response: ResponseBaseModel,
            include_params: dict[str, bool] | None = None
    ) -> list[JsonApiResource]:
        if not include_params:
            return []

        included = await model_response.process_includes(data, include_params)
        all_included = []

        for resources in included.values():
            all_included.extend(resources)

        return all_included

    @staticmethod
    def map_items(data: list[Any] | Sequence[Any]) -> list[JsonApiResource]:
        resources = []
        resource_type = ""
        if len(data) > 0:
            resource_type = data[0].__class__.__name__
        for item in data:
            resources.append(ResponseBaseModel.data_to_resource(item, resource_type))
        return resources

    @staticmethod
    def error(
            status: int,
            title: str,
            detail: str | None = None,
            code: str | None = None,
            source: dict[str, Any] | None = None
    ) -> JsonApiResponse:
        error = JsonApiError(
            status=status,
            title=title,
            detail=detail,
            code=code,
            source=source,
        )
        return JsonApiResponse(errors=[error.model_dump()])

    @staticmethod
    def format_pydantic_error(error: ErrorDetails) -> dict[str, Any]:
        field_path = ""
        if error.get('loc'):
            loc = [str(item) for item in error['loc'] if item != 'body']
            field_path = '.'.join(loc) if loc else ""
        source = {}
        if field_path:
            source['pointer'] = f"/data/attributes/{field_path}"

        return {
            "status": "422",
            "code": error.get('type', 'validation_error'),
            "title": "Validation Error",
            "detail": error.get('msg', 'Invalid input'),
            "source": source if source else None
        }
