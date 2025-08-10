from fastapi import APIRouter, Depends, FastAPI, Header

from src.app.auth.dto.bearer import Bearer
from src.app.auth.dto.confirm_user import ConfirmUserRequest
from src.app.auth.dto.login import LoginRequest
from src.app.auth.dto.re_send_confirm_email import ReSendConfirmEmailRequest
from src.app.auth.dto.sign_up import SignupRequest
from src.core.db.repository import Filter, Oper
from src.core.di.container import Container
from src.core.dto.dto import Message
from src.core.exception.error_no import ErrorNo
from src.core.exception.exceptions import UnauthorizedException
from src.core.http.controller import BaseController
from src.core.http.response.response import JsonApiResponse


class AuthController(BaseController):
    def __init__(self, app: FastAPI, container: Container) -> None:
        super().__init__(container=container)
        router = APIRouter(prefix="/auth", tags=["auth"])
        router.add_api_route(path="/login", endpoint=self.login, methods=["POST"])
        router.add_api_route(path="/signup", endpoint=self.signup, methods=["POST"])
        router.add_api_route(path="/re-send-confirm-email", endpoint=self.re_send_confirm_email, methods=["POST"])
        router.add_api_route(path="/confirm-email", endpoint=self.confirm_user, methods=["GET"])
        router.add_api_route(path="/refresh", endpoint=self.refresh, methods=["POST"])
        app.include_router(router=router)

    async def login(self, req: LoginRequest) -> JsonApiResponse:
        token = await self.container.auth_service().login(email=req.email, password=req.password)

        return await self.response(data=Bearer.from_token(token))

    async def signup(self, req: SignupRequest) -> JsonApiResponse:
        user = await self.container.auth_service().signup(
            first_name=req.first_name, second_name=req.second_name, email=req.email, password=req.password
        )

        return await self.response(data=user)

    async def re_send_confirm_email(self, req: ReSendConfirmEmailRequest) -> JsonApiResponse:
        res = Message(message="Email successfully sent")
        user = await self.container.user_service().one(
            filters=[
                Filter("email", Oper.EQ, req.email),
            ]
        )
        if user is None:
            return await self.response(data=res)

        return await self.response(data=res)

    async def confirm_user(self, req: ConfirmUserRequest = Depends()) -> JsonApiResponse:
        await self.container.auth_service().confirm_user(jwt=req.token)

        return await self.response(data=Message(message="Email successfully confirmed"))

    async def refresh(self, authorization: str = Header(None)) -> JsonApiResponse:
        if authorization is None:
            raise UnauthorizedException(error_no=ErrorNo.AUTHORIZATION_REFRESH_TOKEN_EMPTY, message="Unauthorized!")
        try:
            scheme, jwt = authorization.split(" ", 1)
        except ValueError as e:
            self.log().error(str(e), exc_info=e)
            raise UnauthorizedException(
                error_no=ErrorNo.AUTHORIZATION_REFRESH_TOKEN_INVALID, message="Unauthorized!", inner_exception=e
            )

        if scheme.lower() != "bearer":
            raise UnauthorizedException(
                error_no=ErrorNo.AUTHORIZATION_REFRESH_TOKEN_FORMAT_ERROR, message="Unauthorized!"
            )

        token = await self.container.auth_service().refresh(jwt=jwt)

        return await self.response(data=Bearer.from_token(token))
