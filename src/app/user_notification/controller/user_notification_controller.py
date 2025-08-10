from fastapi import APIRouter, Depends, FastAPI

from src.app.user_notification.data.user_notification_status import UserNotificationStatus
from src.app.user_notification.dto.user_notification import UserNotificationCreateRequest, UserNotificationListRequest
from src.core.db.repository import Filter, Oper, Pagination
from src.core.di.container import Container
from src.core.http.controller import BaseController
from src.core.http.request.state import AuthState, get_auth_state
from src.core.http.response.response import JsonApiResponse


class UserNotificationController(BaseController):
    def __init__(self, app: FastAPI, container: Container) -> None:
        super().__init__(container=container)
        router = APIRouter(prefix="/user-notifications", tags=["user-notifications"])
        router.add_api_route(path="", endpoint=self.user_list, methods=["GET"])
        router.add_api_route(path="", endpoint=self.create, methods=["POST"])
        app.include_router(router=router)

    async def user_list(
        self,
        state: AuthState = Depends(get_auth_state),
        req: UserNotificationListRequest = Depends(),
    ) -> JsonApiResponse:
        notifications = await self.container.user_notification_service().all(
            filters=[
                Filter("user_id", Oper.EQ, state.user.id),
                Filter("status", Oper.EQ, req.status),
            ],
            pagination=Pagination(
                per_page=req.per_page or 10,
                page=req.page or 1,
            ),
        )

        return await self.response(data=notifications, include=req.include)

    async def create(
        self,
        req: UserNotificationCreateRequest,
    ) -> JsonApiResponse:
        notification = req.to_model()
        notification.user_id = 1
        notification.status = UserNotificationStatus.NEW
        user = await self.container.user_notification_service().create(data=notification)

        return await self.response(data=user)
