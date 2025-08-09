from collections.abc import Sequence
from typing import Any

from src.core.db.repository import Paginator
from src.core.http.response.response import JsonApiError, JsonApiResource, JsonApiResponse, ResponseBaseModel


class JsonAPIService:
    def __init__(self) -> None:
        pass

    @staticmethod
    def response(
        data: Any = None,
        errors: list[JsonApiError | dict[str, Any]] | None = None,
        meta: dict[str, Any] | None = None,
        resource_type: str | None = None,
    ) -> JsonApiResponse:
        resources: list[JsonApiResource] | list[dict[str, Any]] | JsonApiResource = []  # noqa
        if data is None and errors is None:
            return JsonApiResponse(meta=meta)
        if resource_type is None:
            resource_type = data.__class__.__name__
        if errors:
            return JsonApiResponse(
                errors=[error.model_dump() if hasattr(error, "model_dump") else error for error in errors],
                meta=meta,
            )
        if isinstance(data, Paginator):
            resources = JsonAPIService.map_items(data.items)
            meta = {
                "total": data.total,
                "page": data.page,
                "perPage": data.per_page,
                "totalPages": data.pages,
            }
        elif isinstance(data, list):
            resources = JsonAPIService.map_items(data)
        else:
            resources = ResponseBaseModel.data_to_resource(data, resource_type)

        return JsonApiResponse(data=resources, meta=meta)

    @staticmethod
    def map_items(data: list | Sequence[Any]) -> list[JsonApiResource]:
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
        detail: str | list[str] | None = None,
        code: str | None = None,
        source: dict[str, Any] | None = None,
    ) -> JsonApiResponse:
        error = JsonApiError(
            status=status,
            title=title,
            detail=detail,
            code=code,
            source=source,
        )
        return JsonApiResponse(errors=[error.model_dump()])
