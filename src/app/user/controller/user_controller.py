from fastapi import APIRouter

from src.app.user.dto.user import UserCreateRequest
from src.core.db.repository import Filter, FilterOperator
from src.core.exception.error_no import ErrorNo
from src.core.exception.exceptions import UnprocessableEntityException
from src.core.http.controller import BaseController
from src.core.http.response.json_api import JsonAPIService
from src.core.http.response.response import JsonApiResponse


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

    async def get_user(self, user_id: int) -> JsonApiResponse:
        user = await self.container.user_service().get_by_id(user_id)
        return JsonAPIService.response(data=user)

    async def create_user(
            self,
            req: UserCreateRequest
    ) -> JsonApiResponse:
        user = await self.container.user_service().one(filters=[
            Filter("email", FilterOperator.EQ, req.email),
        ])
        if user is not None:
            raise UnprocessableEntityException(
                error_no=ErrorNo.USER_EMAIL_ALREADY_EXISTS,
                message="User already exists"
            )

        user = req.to_user()
        user.session = self.container.hash_service().random_string()
        user.hash_password = self.container.hash_service().hash_password(req.password)
        user = await self.container.user_service().create(data=user)

        return JsonAPIService.response(data=user)
