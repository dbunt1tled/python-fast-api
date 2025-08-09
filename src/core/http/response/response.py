from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any

from dependency_injector.containers import Container
from pydantic import BaseModel
from pydantic.alias_generators import to_camel

from src.core.db.repository import Filter, FilterOperator


class JsonApiResource(BaseModel):
    type: str
    id: str
    attributes: dict[str, Any]
    relationships: dict[str, Any] | None = None


class JsonApiResponse(BaseModel):
    data: JsonApiResource | list[JsonApiResource] | list[dict[str, Any]] | dict[str, Any] | None = None
    errors: list[dict[str, Any]] | None = None
    meta: dict[str, Any] | None = None
    included: list[JsonApiResource] | None = None


class JsonApiError(BaseModel):
    id: str | None = None
    status: int
    code: str | None = None
    title: str
    detail: str | list[str] | None = None
    source: dict[str, Any] | None = None


class RelationshipType(str, Enum):
    HAS_ONE = "has_one"
    HAS_MANY = "has_many"
    BELONGS_TO = "belongs_to"


@dataclass
class RelationshipConfig:
    name: str
    service_name: str
    foreign_key: str
    local_key: str = "id"
    service_method: str | None = None
    relationship_type: RelationshipType = RelationshipType.HAS_ONE
    include_in_response: bool = True


@dataclass
class IncludeConfig:
    relationship_name: str
    service_method: str
    params: dict[str, Any] | None = None


class ResponseBaseModel(ABC):
    def __init__(self, container: Container):
        self.container = container

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @property
    @abstractmethod
    def relationships(self) -> dict[str, RelationshipConfig]:
        pass

    def get_resource_type(self) -> str:
        return self.model_name

    def get_service(self, service_name: str) -> Any:
        return getattr(self.container, service_name)()

    async def process_includes(self, data: Any, include_params: dict[str, bool]) -> dict[str, list[JsonApiResource]]:
        included: dict[str, list[JsonApiResource]] = {}
        if not include_params:
            return included

        for param_name, is_include in include_params.items():
            if not is_include:
                continue

            relationship_name = self._param_to_relationship_name(param_name)
            if relationship_name not in self.relationships:
                continue

            relationship_config = self.relationships[relationship_name]
            if isinstance(data, (list, Sequence)):
                included[relationship_name] = await self._process_relationship_for_list(data, relationship_config)
            else:
                included[relationship_name] = await self._process_relationship_for_item(data, relationship_config)

        return included

    @staticmethod
    def _param_to_relationship_name(param_name: str) -> str:
        if param_name.startswith("with"):
            param_name = param_name.replace("with", "").strip("_")
        return param_name

    async def _process_relationship_for_list(
        self, data_list: list[Any] | Sequence[Any], config: RelationshipConfig
    ) -> list[JsonApiResource]:
        if not data_list:
            return []

        ids = []
        for item in data_list:
            if hasattr(item, config.local_key):
                ids.append(getattr(item, config.local_key))

        if not ids:
            return []

        service = self.get_service(config.service_name)

        if config.service_method:
            related_data = await getattr(service, config.service_method)(ids)
        else:
            if config.relationship_type == RelationshipType.HAS_MANY:
                related_data = await service.all(
                    filters=[
                        Filter(config.foreign_key, FilterOperator.IN, ids),
                    ],
                )
            else:
                related_data = await service.all(
                    filters=[
                        Filter("id", FilterOperator.IN, ids),
                    ],
                )

        resources = []
        for item in related_data:
            resources.append(self.data_to_resource(item))

        return resources

    async def _process_relationship_for_item(self, data: Any, config: RelationshipConfig) -> list[JsonApiResource]:
        if not hasattr(data, config.local_key):
            return []

        local_id = getattr(data, config.local_key)
        service = self.get_service(config.service_name)
        if config.service_method:
            related_data = await getattr(service, config.service_method)(local_id)
        else:
            if config.relationship_type == RelationshipType.HAS_MANY:
                related_data = await service.all(
                    filters=[
                        Filter(config.foreign_key, FilterOperator.EQ, local_id),
                    ],
                )
            else:
                related_data = await service.get_by_id(local_id)

        if not related_data:
            return []

        if isinstance(related_data, list):
            return [self.data_to_resource(item) for item in related_data]
        else:
            return [self.data_to_resource(related_data)]

    def add_relationships_to_resource(
        self, resource: JsonApiResource, data: Any, included: dict[str, list[JsonApiResource]]
    ) -> JsonApiResource:
        if not included:
            return resource

        relationships: dict[str, dict[str, Any]] = {}

        for relationship_name, related_resources in included.items():
            if relationship_name not in self.relationships:
                continue

            config = self.relationships[relationship_name]

            if config.relationship_type == RelationshipType.HAS_MANY:
                relationships[relationship_name] = {
                    "data": [
                        {"type": res.type, "id": res.id}
                        for res in related_resources
                        if self._is_related_to_resource(data, res, config)
                    ]
                }
            else:
                related_res = self._find_related_resource(data, related_resources, config)
                if related_res:
                    relationships[relationship_name] = {"data": {"type": related_res.type, "id": related_res.id}}

        if relationships:
            resource.relationships = relationships

        return resource

    @staticmethod
    def _is_related_to_resource(data: Any, resource: JsonApiResource, config: RelationshipConfig) -> bool:
        if not hasattr(data, config.local_key):
            return False

        local_value = getattr(data, config.local_key)
        foreign_key_value = to_camel(config.foreign_key)
        if hasattr(resource, "attributes") and foreign_key_value in resource.attributes:
            return str(resource.attributes[foreign_key_value]) == str(local_value)

        return False

    @staticmethod
    def _find_related_resource(
        data: Any, resources: list[JsonApiResource], config: RelationshipConfig
    ) -> JsonApiResource | None:
        if not hasattr(data, config.local_key):
            return None

        local_value = str(getattr(data, config.local_key))
        for resource in resources:
            if resource.id == local_value:
                return resource

        return None

    @staticmethod
    def data_to_resource(data: Any, resource_type: str | None = None) -> JsonApiResource:
        if resource_type is None:
            resource_type = data.__class__.__name__
        return JsonApiResource(
            type=resource_type,
            id=str(data.id if hasattr(data, "id") else ""),
            attributes=data.to_dict(camel=True)
            if hasattr(data, "to_dict")
            else data.model_dump(by_alias=True)
            if hasattr(data, "model_dump")
            else data,
        )
