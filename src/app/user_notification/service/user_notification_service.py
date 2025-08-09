from collections.abc import Sequence
from typing import Any

from src.app.user_notification.data.user_notification_status import UserNotificationStatus
from src.app.user_notification.model.user_notification import UserNotification
from src.app.user_notification.repository.user_notification_repository import UserNotificationRepository
from src.core.db.repository import Filter, FilterOperator, OrderBy, Pager, Pagination, Paginator


class UserNotificationService:
    def __init__(self, user_notification_repository: UserNotificationRepository) -> None:
        self.user_notification_repository = user_notification_repository

    async def get_by_id(self, id_value: int) -> UserNotification:
        return await self.user_notification_repository.get_by_id(id_value=id_value)

    async def find_by_id(self, id_value: int) -> UserNotification | None:
        return await self.user_notification_repository.find_by_id(id_value=id_value)

    async def create(self, data: dict[str, Any] | UserNotification) -> UserNotification:
        return await self.user_notification_repository.create(data=data)

    async def update(self, id_value: int, data: dict[str, Any]) -> UserNotification:
        return await self.user_notification_repository.update(id_value=id_value, data=data)

    async def one(
        self,
        filters: list[Filter] | None = None,
        order_by: list[OrderBy] | None = None,
    ) -> UserNotification | None:
        return await self.user_notification_repository.find_one(filters=filters, order_by=order_by)

    async def all(
        self,
        filters: list[Filter] | None = None,
        order_by: list[OrderBy] | None = None,
        pagination: Pagination | None = None,
        pager: Pager | None = None,
    ) -> Sequence[UserNotification] | Paginator[UserNotification]:
        return await self.user_notification_repository.find_all(
            filters=filters, order_by=order_by, pagination=pagination, pager=pager
        )

    async def new_by_user_id(self, id_value: int | list[int]) -> Sequence[UserNotification]:
        return await self.all(  # type: ignore
            filters=[
                Filter("user_id", FilterOperator.IN if isinstance(id_value, list) else FilterOperator.EQ, id_value),
                Filter("status", FilterOperator.EQ, UserNotificationStatus.NEW),
            ],
        )
