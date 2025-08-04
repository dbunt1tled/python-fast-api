
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from src.core.exception.error_no import ErrorNo
from src.core.exception.exceptions import UnauthorizedException
from src.core.service.hash_service import HashService


class XApiKeyAuth(BaseHTTPMiddleware):
    INCLUDED_PATHS: list[str] = [

    ]

    def __init__(
            self,
            app: ASGIApp,
            hash_service: HashService,
    ) -> None:
        super().__init__(app=app)
        self.hash_service = hash_service

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not self._is_included_path(request.url.path):
            return await call_next(request)

        authorization = request.headers.get("X-Api-Key")
        if not authorization:
            raise UnauthorizedException(error_no=ErrorNo.AUTHORIZATION_X_API_KEY_EMPTY, message="Unauthorized!")

        if not self.hash_service.verify_x_api_key(key=authorization):
            raise UnauthorizedException(error_no=ErrorNo.AUTHORIZATION_X_API_KEY_INVALID, message="Unauthorized!")

        return await call_next(request)

    @staticmethod
    def _is_included_path(path: str) -> bool:
        for excluded_path in XApiKeyAuth.INCLUDED_PATHS:
            if path.startswith(excluded_path):
                return True
        return False
