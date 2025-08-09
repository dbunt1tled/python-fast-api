import traceback
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.app.auth.controller.auth_controller import AuthController
from src.app.user.controller.user_controller import UserController
from src.app.user_notification.controller.user_notification_controller import UserNotificationController
from src.core.di.container import Container
from src.core.enum.env import Env
from src.core.exception.error_no import ErrorNo
from src.core.exception.exceptions import DomainException
from src.core.http.middleware.auth_bearer import AuthBearer
from src.core.http.middleware.body_save import BodySave
from src.core.http.middleware.logging import LoggingRequest
from src.core.http.middleware.x_api_key_auth import XApiKeyAuth
from src.core.http.response.api_response_service import ApiResponseService
from src.core.http.response.json_api import JsonAPIService
from src.core.service.functions import extract_body, filter_headers


@asynccontextmanager
async def lifespan(api: FastAPI) -> AsyncGenerator[None]:
    container = Container()
    await container.rmq_producer().initialize()
    AuthController(app=api, container=container)
    UserController(app=api, container=container)
    UserNotificationController(app=api, container=container)
    yield
    await container.db_config().close()
    container.unwire()


app = FastAPI(
    lifespan=lifespan,
    title="Simple API",
    description="API for startup project.\n\n",
    version="1.0.0",
)
di = Container()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "X-Total-Count",
        "X-Per-Page",
        "X-Current-Page",
        "X-Total-Pages",
        "X-User-Role",
    ],
)
app.add_middleware(
    AuthBearer,
    hash_service=di.hash_service(),
    user_service=di.user_service(),
)
app.add_middleware(XApiKeyAuth, hash_service=di.hash_service())
if di.app_config().log_request:
    app.add_middleware(LoggingRequest, logger=di.log_request())
app.add_middleware(BodySave, hash_service=di.hash_service())


async def exception_handler(request: Request, e: Exception) -> JSONResponse:
    di = Container()

    req = {
        "method": request.method,
        "url": str(request.url),
        "headers": filter_headers(request=request),
        "ip": request.client.host if request.client else None,
        "body": extract_body(request=request, secure=True),
    }
    if isinstance(e, ValueError):
        di.log().error(message=f"ValueError: {e}", error=e.__dict__, request=req)
        raise ValueError(e.args)

    if isinstance(e, RequestValidationError):
        error = ApiResponseService.format_pydantic_error(errors=e.errors(), env=di.app_config().environment)
        di.log().error(message=f"RequestValidationError: {e}", error=str(error), request=req)
    elif isinstance(e, DomainException):
        e_data = e.as_dict()
        if di.app_config().environment == Env.PRODUCTION:
            e_data["source"] = None
        error = JsonAPIService.response(errors=[e_data])
        di.log().error(message=f"{e.__class__.__name__}: {e}", error=str(e_data), request=req)
    else:
        error = JsonAPIService.error(
            status=500,
            title="Internal Server Error",
            detail=str(e),
            code=str(ErrorNo.GENERAL_ERROR.value),
            source={"traceback": traceback.format_exc()} if di.app_config().environment != Env.PRODUCTION else None,
        )
        di.log().error(message=f"{e.__class__.__name__}: {e}", error=str(error.model_dump()), request=req)
    if error is None or error.errors is None:
        di.log().error(message=f"{e.__class__.__name__}: {e}", error=None, request=req)
        return JSONResponse(
            status_code=500,
            content={"status": 500, "title": "Internal Server Error", "detail": str(e)},
        )
    return JSONResponse(
        status_code=error.errors[0]["status"],
        content=error.model_dump(exclude_none=True),
    )


if RequestValidationError in app.exception_handlers:
    del app.exception_handlers[RequestValidationError]

app.add_exception_handler(Exception, exception_handler)
