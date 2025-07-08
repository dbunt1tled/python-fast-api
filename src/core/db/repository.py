from abc import ABC
from collections.abc import Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, TypeVar

from sqlalchemy import and_, delete, func, select, update
from sqlalchemy.sql import Select, Update, Delete

from src.core.db.asmysql import MyDatabaseConfig
from src.core.db.entity import Entity
from src.core.exception.error_no import ErrorNo
from src.core.exception.exceptions import DomainException

T = TypeVar('T', bound=Entity)

class FilterOperator(Enum):
    EQ = "eq"
    NE = "ne"
    GT = "gt"
    LT = "lt"
    GTE = "gte"
    LTE = "lte"
    LIKE = "like"
    ILIKE = "ilike"
    IN = "in"
    NOT_IN = "not_in"
    BETWEEN = "between"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    CONTAINS = "contains"
    STARTSWITH = "startswith"
    ENDSWITH = "endswith"
    # JSON operators
    JSON_EXTRACT = "json_extract"          # Extract value by path: field->'$.path'
    JSON_EXTRACT_TEXT = "json_extract_text" # Extract text value: field->>'$.path'
    JSON_CONTAINS = "json_contains"        # Check if JSON contains value
    JSON_CONTAINS_PATH = "json_contains_path"  # Check if path exists
    JSON_ARRAY_CONTAINS = "json_array_contains"  # Check if array contains value
    JSON_LENGTH = "json_length"            # Get length of JSON array/object

@dataclass
class Filter:
    field: str
    operator: FilterOperator
    value: Any = None
    json_path: str|None = None  # For JSON operations like '$.roles[*].name'

    def __post_init__(self) -> None:
        # Validate filter based on operator
        if self.operator in [FilterOperator.IS_NULL, FilterOperator.IS_NOT_NULL]:
            self.value = None
        elif self.operator == FilterOperator.BETWEEN and (
                not isinstance(self.value, (list, tuple)) or len(self.value) != 2
        ):
            raise ValueError("BETWEEN operator requires exactly two values")
        elif self.operator in [
            FilterOperator.JSON_EXTRACT,
            FilterOperator.JSON_EXTRACT_TEXT,
            FilterOperator.JSON_CONTAINS_PATH,
            FilterOperator.JSON_LENGTH
        ] and not self.json_path:
            raise ValueError(f"{self.operator.value} requires json_path parameter")


@dataclass
class OrderBy:
    field: str
    desc: bool = False


@dataclass
class Pagination:
    limit: int | None = None
    offset: int | None = None

    @property
    def page(self) -> int | None:
        if self.offset is None or self.limit is None or self.limit == 0:
            return None
        return (self.offset // self.limit) + 1


class BaseRepository(ABC, Generic[T]):
    def __init__(
            self,
            db_config: MyDatabaseConfig,
            model: type[T],
            id_field: str = "id"
    ):
        self._db_config = db_config
        self._model = model
        self._id_field = id_field

    async def get_by_id(
            self,
            id_value: Any,
    ) -> T:
        obj = await self.find_by_id(id_value)
        if obj is None:
            raise DomainException(
                error_no=ErrorNo.REPOSITORY_DATA_BY_ID_NOT_FOUND,
                message=f"{self._model.__name__} with {self._id_field}={id_value} not found"
            )
        return obj

    async def find_by_id(
            self,
            id_value: Any,
    ) -> T | None:
        query = select(self._model).where(getattr(self._model, self._id_field) == id_value)
        async with self.get_session() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()


    async def create(self, data: dict[str, Any] | T) -> T:
        if isinstance(data, dict):
            entity = self._model(**data)
        else:
            entity = data
        async with self.get_session() as session:
            session.add(entity)
            await session.flush()
            await session.refresh(entity)
            return entity

    async def update(
            self,
            id_value: Any,
            data: dict[str, Any] | T,
    ) -> T:
        if isinstance(data, dict):
            d = data
        else:
            d = data.__dict__

        entity = await self.get_by_id(id_value)

        for field, value in d.items():
            if hasattr(entity, field):
                setattr(entity, field, value)
        async with self.get_session() as session:
            await session.flush()
            await session.refresh(entity)
            return entity

    async def update_many(
            self,
            filters: list[Filter],
            update_data: dict[str, Any]
    ) -> int:
        query = update(self._model)
        query = self._apply_filters(query, filters)
        query = query.values(**update_data)

        async with self.get_session() as session:
            result = await session.execute(query)
            return result.rowcount or 0

    async def delete(self, id_value: Any) -> bool:
        db_obj = await self.find_by_id(id_value)
        if db_obj is None:
            return False

        async with self.get_session() as session:
            await session.delete(db_obj)
            return True

    async def delete_many(self, filters: list[Filter]) -> int:
        query = delete(self._model)
        query = self._apply_filters(query, filters)

        async with self.get_session() as session:
            result = await session.execute(query)
            return result.rowcount or 0

    async def find_all(
            self,
            filters: list[Filter] | None = None,
            order_by: list[OrderBy] | None = None,
            pagination: Pagination | None = None,
    ) -> Sequence[T]:
        query = select(self._model)

        if filters:
            query = self._apply_filters(query, filters)

        if order_by:
            query = self._apply_ordering(query, order_by)

        if pagination:
            if pagination.limit is not None:
                query = query.limit(pagination.limit)
            if pagination.offset is not None:
                query = query.offset(pagination.offset)
        async with self.get_session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    async def find_one(
            self,
            filters: list[Filter] | None = None,
            order_by: list[OrderBy] | None = None,
    ) -> T | None:
        query = select(self._model)

        if filters:
            query = self._apply_filters(query, filters)

        if order_by:
            query = self._apply_ordering(query, order_by)

        query = query.limit(1)

        async with self.get_session() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def count(self, filters: list[Filter] | None = None) -> int:
        query = select(func.count()).select_from(self._model)

        if filters:
            query = self._apply_filters(query, filters)

        async with self.get_session() as session:
            result = await session.execute(query)
            return result.scalar() or 0

    async def exists(self, filters: list[Filter]) -> bool:
        query = select(1)
        query = query.select_from(self._model)
        query = self._apply_filters(query, filters)
        query = query.limit(1)

        async with self.get_session() as session:
            result = await session.execute(query)
            return result.first() is not None

    def _apply_filters(self, query: Select| Update | Delete, filters: list[Filter]) -> Select| Update | Delete:
        conditions = []

        for filter_item in filters:
            field = getattr(self._model, filter_item.field)

            if filter_item.operator == FilterOperator.EQ:
                conditions.append(field == filter_item.value)
            elif filter_item.operator == FilterOperator.NE:
                conditions.append(field != filter_item.value)
            elif filter_item.operator == FilterOperator.GT:
                conditions.append(field > filter_item.value)
            elif filter_item.operator == FilterOperator.LT:
                conditions.append(field < filter_item.value)
            elif filter_item.operator == FilterOperator.GTE:
                conditions.append(field >= filter_item.value)
            elif filter_item.operator == FilterOperator.LTE:
                conditions.append(field <= filter_item.value)
            elif filter_item.operator == FilterOperator.LIKE:
                conditions.append(field.like(filter_item.value))
            elif filter_item.operator == FilterOperator.ILIKE:
                conditions.append(field.ilike(filter_item.value))
            elif filter_item.operator == FilterOperator.IN:
                conditions.append(field.in_(filter_item.value))
            elif filter_item.operator == FilterOperator.NOT_IN:
                conditions.append(~field.in_(filter_item.value))
            elif filter_item.operator == FilterOperator.BETWEEN:
                conditions.append(field.between(filter_item.value[0], filter_item.value[1]))
            elif filter_item.operator == FilterOperator.IS_NULL:
                conditions.append(field.is_(None))
            elif filter_item.operator == FilterOperator.IS_NOT_NULL:
                conditions.append(field.is_not(None))
            elif filter_item.operator == FilterOperator.CONTAINS:
                conditions.append(field.contains(filter_item.value))
            elif filter_item.operator == FilterOperator.STARTSWITH:
                conditions.append(field.startswith(filter_item.value))
            elif filter_item.operator == FilterOperator.ENDSWITH:
                conditions.append(field.endswith(filter_item.value))
            # JSON operators
            elif filter_item.operator == FilterOperator.JSON_EXTRACT:
                # Extract value: field->'$.path' = value
                conditions.append(field.op('->')( filter_item.json_path) == filter_item.value)
            elif filter_item.operator == FilterOperator.JSON_EXTRACT_TEXT:
                # Extract text value: field->>'$.path' = value
                conditions.append(field.op('->>')( filter_item.json_path) == filter_item.value)
            elif filter_item.operator == FilterOperator.JSON_CONTAINS:
                # Check if JSON contains value: JSON_CONTAINS(field, value)
                from sqlalchemy import func
                conditions.append(func.json_contains(field, filter_item.value))
            elif filter_item.operator == FilterOperator.JSON_CONTAINS_PATH:
                # Check if path exists: JSON_CONTAINS_PATH(field, path)
                from sqlalchemy import func
                conditions.append(func.json_contains_path(field, filter_item.json_path))
            elif filter_item.operator == FilterOperator.JSON_ARRAY_CONTAINS:
                # Check if JSON array contains value
                from sqlalchemy import func
                if filter_item.json_path:
                    # Check specific path in array
                    conditions.append(func.json_contains(
                        field.op('->')( filter_item.json_path),
                        f'"{filter_item.value}"' if isinstance(filter_item.value, str) else filter_item.value
                    ))
                else:
                    # Check entire field
                    conditions.append(func.json_contains(field, filter_item.value))
            elif filter_item.operator == FilterOperator.JSON_LENGTH:
                # Get length of JSON array/object: JSON_LENGTH(field, path) = value
                from sqlalchemy import func
                if filter_item.json_path:
                    conditions.append(func.json_length(field, filter_item.json_path) == filter_item.value)
                else:
                    conditions.append(func.json_length(field) == filter_item.value)

        if conditions:
            query = query.where(and_(*conditions))

        return query

    def _apply_ordering(self, query: Select, order_by: list[OrderBy]) -> Select:
        order_clauses = []

        for order_item in order_by:
            field = getattr(self._model, order_item.field)
            if order_item.desc:
                order_clauses.append(field.desc())
            else:
                order_clauses.append(field.asc())

        if order_clauses:
            query = query.order_by(*order_clauses)

        return query

    async def raw_query(self, query: str, params: dict[str, Any] | None = None) -> Any:
        from sqlalchemy import text
        async with self.get_session() as session:
            result = await session.execute(text(query), params or {})
            return result

    @asynccontextmanager
    async def get_session(self):
        async with self._db_config.session() as session:
            yield session
