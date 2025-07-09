from fastapi import APIRouter

from src.app.user.data.role import Role
from src.app.user.data.user_status import UserStatus
from src.app.user.model.dto import UserCreateRequest
from src.app.user.model.user import User
from src.core.db.repository import Filter, FilterOperator
from src.core.exception.error_no import ErrorNo
from src.core.exception.exceptions import UnprocessableEntityException
from src.core.http.controller import BaseController
from src.core.http.response.json_api import JsonAPIService


class UserController(BaseController):

    def __init__(self) -> None:
        super().__init__()
        self.router = APIRouter(prefix="/users")
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.router.get("")(self.get_users)
        self.router.post("")(self.create_user)
        self.router.get("/{user_id}")(self.get_user)

    async def get_users(self):
        u = await self.container.user_service().user_service().all()
        return u

    async def get_user(self, user_id: int):
        user = await self.container.user_service().get_by_id(user_id)
        return JsonAPIService.response(data=user)

    async def create_user(
            self,
            user_request: UserCreateRequest
    ):
        user = await self.container.user_service().one(filters=[
            Filter("email", FilterOperator.EQ, user_request.email),
        ])
        if user is not None:
            raise UnprocessableEntityException(
                error_no=ErrorNo.USER_EMAIL_ALREADY_EXISTS,
                message="User already exists"
            )

        user = User(
            first_name=user_request.first_name,
            second_name=user_request.second_name,
            email=user_request.email,
            hash=self.container.hash_service().hash_password(user_request.password),
            status=UserStatus.PENDING,
            roles=[Role.ADMIN],
        )
        user = await self.container.user_service().create(data=user)

        return JsonAPIService.response(data=user)
