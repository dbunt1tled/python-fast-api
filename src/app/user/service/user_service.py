from collections.abc import Sequence
from typing import Any

from src.app.user.model.user import User
from src.app.user.repository.user_repository import UserRepository
from src.core.db.repository import Filter, OrderBy, Pager, Pagination, Paginator


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def get_by_id(self, uid: int) -> User:
        return await self.user_repository.get_by_id(uid=uid)

    async def find_by_id(self, uid: int) -> User | None:
        return await self.user_repository.find_by_id(uid=uid)

    async def create(self, data: dict[str, Any] | User) -> User:
        return await self.user_repository.create(data=data)

    async def update(self, uid: int, data: dict[str, Any]) -> User:
        return await self.user_repository.update(uid=uid, data=data)

    async def one(
        self,
        filters: list[Filter] | None = None,
        order_by: list[OrderBy] | None = None,
    ) -> User | None:
        return await self.user_repository.find_one(filters=filters, order_by=order_by)

    async def all(
        self,
        filters: list[Filter] | None = None,
        order_by: list[OrderBy] | None = None,
        pagination: Pagination | None = None,
        pager: Pager | None = None,
    ) -> Sequence[User] | Paginator[User]:
        return await self.user_repository.find_all(
            filters=filters, order_by=order_by, pagination=pagination, pager=pager
        )
