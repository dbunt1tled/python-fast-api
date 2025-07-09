from typing import Any

from sqlalchemy.orm import DeclarativeBase
from pydantic.alias_generators import to_camel


class Entity(DeclarativeBase):
    def to_dict(self, camel: bool = False) -> dict[str, Any]:
        return {to_camel(col.name) if camel else col.name: getattr(self, col.name) for col in self.__table__.columns}
