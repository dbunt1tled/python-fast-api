import json
import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.core.log.log import Log
from src.core.service.functions import filter_params


class LoggingRequest(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, logger: Log) -> None:
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        body_request = ""
        if request.method in ["POST", "PUT", "PATCH"]:
            if not hasattr(request.state, 'body'):
                return await call_next(request)
            body = request.state.body
            body_request = body.decode('utf-8', errors='ignore')
            try:
                parsed_json = json.loads(body_request)
                parsed_json = filter_params(parsed_json)
                body_request = json.dumps(parsed_json, ensure_ascii=False, indent=2)
            finally:
                pass
        try:
            response = await call_next(request)
            res_body = [section async for section in response.body_iterator]
            response.body_iterator = iterate_in_threadpool(iter(res_body))
            body_response = res_body[0].decode()
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_request_full(
                request=request,
                status_code=response.status_code,
                body_request=body_request,
                body_response=body_response,
                duration_ms=duration_ms
            )


            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            self.logger.log_request_exception(
                request=request,
                e=e,
                body_request=body_request,
                duration_ms=duration_ms
            )
            raise e
