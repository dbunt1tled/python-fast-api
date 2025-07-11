import logging
from fastapi import APIRouter, Depends, Header

from src.app.auth.dto.bearer import Bearer
from src.app.auth.dto.confirm_user import ConfirmUserRequest
from src.app.auth.dto.login import LoginRequest
from src.app.auth.dto.re_send_confirm_email import ReSendConfirmEmailRequest
from src.app.auth.dto.sign_up import SignupRequest
from src.core.db.repository import Filter, FilterOperator
from src.core.dto.dto import Message
from src.core.exception.exceptions import UnauthorizedException
from src.core.http.controller import BaseController
from src.core.http.response.json_api import JsonAPIService
from src.core.http.response.response import JsonApiResponse


class AuthController(BaseController):
    def __init__(self) -> None:
        super().__init__()
        self.router = APIRouter(prefix="/auth")
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.router.post("/login")(self.login)
        self.router.post("/signup")(self.signup)
        self.router.post("/re-send-confirm-email")(self.re_send_confirm_email)
        self.router.get("/confirm-email")(self.confirm_user)
        self.router.post("/refresh")(self.refresh)
        self.logger = logging.getLogger(__name__)

    async def login(self, req: LoginRequest) -> JsonApiResponse:
        token = await self.container.auth_service().login(
            email=req.email,
            password=req.password
        )

        return JsonAPIService.response(data=Bearer.from_token(token))

    async def signup(self, req: SignupRequest) -> JsonApiResponse:
        user = await self.container.auth_service().signup(
            first_name=req.first_name,
            second_name=req.second_name,
            email=req.email,
            password=req.password
        )

        return JsonAPIService.response(data=user)

    async def re_send_confirm_email(self, req: ReSendConfirmEmailRequest) -> JsonApiResponse:
        res = Message(message="Email successfully sent")
        user = await self.container.user_service().one(filters=[
            Filter("email", FilterOperator.EQ, req.email),
        ])
        if user is None:
            return JsonAPIService.response(data=res)

        return JsonAPIService.response(data=res)

    async def confirm_user(self, req: ConfirmUserRequest = Depends()) -> JsonApiResponse:

        await self.container.auth_service().confirm_user(jwt=req.token)

        return JsonAPIService.response(data=Message(message="Email successfully confirmed"))


    async def refresh(self, authorization: str = Header(None)) -> JsonApiResponse:
        if authorization is None:
            raise UnauthorizedException(
                error_no=ErrorNo.AUTHORIZATION_REFRESH_TOKEN_EMPTY,
                message="Unauthorized!"
            )
        try:
            scheme, jwt = authorization.split(" ", 1)
            if scheme.lower() != "bearer":
                raise UnauthorizedException(error_no=ErrorNo.AUTHORIZATION_REFRESH_TOKEN_FORMAT_ERROR, message="Unauthorized!")
        except ValueError as e:
            self.logger.error(str(e), exc_info=e)
            raise UnauthorizedException(error_no=ErrorNo.AUTHORIZATION_REFRESH_TOKEN_INVALID, message="Unauthorized!")

        token = await self.container.auth_service().refresh(jwt=jwt)

        return JsonAPIService.response(data=Bearer.from_token(token))
