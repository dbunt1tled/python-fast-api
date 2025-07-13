from fastapi import APIRouter, Depends

from src.app.user_notification.data.user_notification_status import UserNotificationStatus
from src.app.user_notification.dto.user_notification import UserNotificationCreateRequest, UserNotificationListRequest
from src.core.db.repository import Filter, FilterOperator, Pagination
from src.core.http.controller import BaseController
from src.core.http.request.state import AuthState, get_auth_state
from src.core.http.response.json_api import JsonAPIService
from src.core.http.response.response import JsonApiResponse


class UserNotificationController(BaseController):

    def __init__(self) -> None:
        super().__init__()
        self.router = APIRouter(prefix="/user-notifications")
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.router.get("")(self.user_list)
        self.router.post("")(self.create)

    async def user_list(
            self,
            state: AuthState = Depends(get_auth_state),
            req: UserNotificationListRequest = Depends()
    ) -> JsonApiResponse:
        notifications = await self.container.user_notification_service().all(
            filters=[
                Filter("user_id", FilterOperator.EQ, state.user.id),
                Filter("status", FilterOperator.EQ, req.status),
            ],
            pagination=Pagination(
                per_page=req.per_page or 10,
                page= req.page or 1,
            )
        )

        return await self.api_response.response(data=notifications, include=req.include)

    async def create(
            self,
            req: UserNotificationCreateRequest,
    ) -> JsonApiResponse:
        notification = req.to_model()
        notification.user_id = 1
        notification.status = UserNotificationStatus.NEW
        user = await self.container.user_notification_service().create(data=notification)

        return JsonAPIService.response(data=user)
