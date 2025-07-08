from typing import Any

from sqlalchemy.orm import DeclarativeBase


class Entity(DeclarativeBase):
    def to_dict(self) -> dict[str, Any]:
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}
