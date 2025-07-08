from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from src.app.user.data.user_status import UserStatus
from src.app.user.service.user_service import UserService
from src.core.exception.error_no import ErrorNo
from src.core.exception.exceptions import UnauthorizedException
from src.core.service.hash import HashService


class AuthBearer(BaseHTTPMiddleware):
    EXCLUDED_PATHS = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/auth/login",
        "/auth/refresh",
        "/auth/register",
        "/health"
    ]

    def __init__(
            self,
            app: ASGIApp,
            user_service: UserService,
            hash_service: HashService
    ) -> None:
        super().__init__(app=app)
        self.hash_service = hash_service
        self.user_service = user_service
        self.bearer_scheme = HTTPBearer(auto_error=False)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if AuthBearer._is_excluded_path(request.url.path):
            return await call_next(request)

        authorization = request.headers.get("Authorization")
        if not authorization:
            raise UnauthorizedException(error_no=ErrorNo.AUTHORIZATION_HEADER_NOT_FOUND, message="Unauthorized!")

        try:
            scheme, token = authorization.split(" ", 1)
            if scheme.lower() != "bearer":
                raise UnauthorizedException(error_no=ErrorNo.AUTHORIZATION_BEARER_FORMAT_ERROR, message="Unauthorized!")
        except ValueError:
            raise UnauthorizedException(error_no=ErrorNo.AUTHORIZATION_BEARER_INVALID, message="Unauthorized!")

        payload = self.hash_service.verify_token(token)
        if not payload:
            raise UnauthorizedException(error_no=ErrorNo.AUTHORIZATION_BEARER_TOKEN_INVALID_OR_EXPIRED, message="Unauthorized!")

        user = await self.user_service.get_by_id(payload.get("user_id"))
        if not user or not user.status == UserStatus.ACTIVE:
            raise UnauthorizedException(error_no=ErrorNo.AUTHORIZATION_USER_NOT_FOUND, message="Unauthorized!")
        request.state.user = user
        request.state.is_authenticated = True

        return await call_next(request)

    @staticmethod
    def _is_excluded_path(path: str) -> bool:
        for excluded_path in AuthBearer.EXCLUDED_PATHS:
            if path.startswith(excluded_path):
                return True
        return False
