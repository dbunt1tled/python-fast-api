from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.core.service.hash_service import HashService


class BodySave(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        hash_service: HashService,
    ) -> None:
        super().__init__(app=app)
        self.hash_service = hash_service

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        body = await request.body()
        request_id = str(self.hash_service.uuid4())
        request.state.request_id = request_id
        request.state.body = body
        return await call_next(request)
