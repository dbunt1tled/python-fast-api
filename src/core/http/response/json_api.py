from typing import Any, Sequence

from pydantic_core import ErrorDetails

from src.core.db.repository import Paginator
from src.core.http.response.response import JsonApiError, JsonApiResource, JsonApiResponse


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
        if data is None and errors is None:
            return JsonApiResponse(meta=meta)
        if resource_type is None:
            resource_type = data.__class__.__name__
        if errors:
            return JsonApiResponse(
                errors=[error.model_dump() if hasattr(error, "model_dump") else error for error in errors],
                meta=meta,
            )
        resources: list[JsonApiResource] | JsonApiResource = []
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
            resources = JsonAPIService._data_to_resource(data, resource_type)

        return JsonApiResponse(data=resources, meta=meta)

    @staticmethod
    def map_items(data : list|  Sequence[Any]) -> list[JsonApiResource]:
        resources = []
        resource_type = ""
        if len(data) > 0:
            resource_type = data[0].__class__.__name__
        for item in data:
            resources.append(JsonAPIService._data_to_resource(item, resource_type))
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
    def _data_to_resource(data : Any, resource_type: str | None = None) -> JsonApiResource:
        if resource_type is None:
            resource_type = data.__class__.__name__
        a =  hasattr(data, "model_dump")
        return JsonApiResource(
            type=str(resource_type),
            id=str(data.id if hasattr(data, "id") else ""),
            attributes= data.to_dict(camel=True) if hasattr(data, "to_dict") else data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data
        )

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
