from fastapi import APIRouter

from src.app.auth.controller.model.dto import LoginRequest, AccessApp
from src.app.user.data.role import Role
from src.app.user.data.user_status import UserStatus
from src.app.user.model.dto import UserCreateRequest
from src.app.user.model.user import User
from src.app.user.service.user_service import UserService
from src.core.db.repository import Filter, FilterOperator
from src.core.exception.error_no import ErrorNo
from src.core.exception.exceptions import UnprocessableEntityException, UnauthorizedException
from src.core.http.controller import BaseController
from src.core.http.response.json_api import JsonAPIService
from src.core.service.hash import HashService


class AuthController(BaseController):
    def __init__(self) -> None:
        super().__init__()
        self.router = APIRouter(prefix="/auth")
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.router.post("/login")(self.login)
        self.router.post("/refresh")(self.refresh)

    async def login(self, login_request: LoginRequest):
        user = await self.container.user_service().one(filters=[
            Filter("email", FilterOperator.EQ, login_request.email),
        ])
        if user is None:
            raise UnauthorizedException(
                error_no=ErrorNo.USER_EMAIL_NOT_FOUND,
                message="Unauthorized!"
            )
        if user.status != UserStatus.ACTIVE:
            raise UnauthorizedException(
                error_no=ErrorNo.USER_STATUS_NOT_ACTIVE,
                message="Unauthorized!"
            )

        if not self.container.hash_service().verify_password(
                password=login_request.password,
                hashed_password=user.hash
        ):
            raise UnauthorizedException(
                error_no=ErrorNo.AUTHORIZATION_USER_PASSWORD_INVALID,
                message="Unauthorized!"
            )

        token = self.container.hash_service().create_token_bearer(user=user)

        return JsonAPIService.response(data=AccessApp.from_token(token))


    async def refresh(self, user_id: int):
        return await self.container.user_service().get_by_id(user_id)