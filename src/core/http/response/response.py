from typing import Any

from pydantic import BaseModel


class JsonApiResource(BaseModel):
    type: str
    id: str
    attributes: dict[str, Any]
    relationships: dict[str, Any] | None = None

class JsonApiResponse(BaseModel):
    data: JsonApiResource | list[JsonApiResource] | None = None
    errors: list[dict[str, Any]] | None = None
    meta: dict[str, Any] | None = None

class JsonApiError(BaseModel):
    id: str | None = None
    status: int
    code: str | None = None
    title: str
    detail: str | None = None
    source: dict[str, Any] | None = None


