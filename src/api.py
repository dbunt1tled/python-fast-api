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
from src.core.exception.error_no import ErrorNo
from src.core.exception.exceptions import DomainException
from src.core.http.middleware.auth_bearer import AuthBearer
from src.core.http.response.api_response_service import ApiResponseService
from src.core.http.response.json_api import JsonAPIService
from src.core.http.response.response import JsonApiResponse


@asynccontextmanager
async def lifespan(api: FastAPI) -> AsyncGenerator[None]:
    container = Container()
    AuthController(app=api, container=container)
    UserController(app=api, container=container)
    UserNotificationController(app=api, container=container)
    yield

    # Shutdown
    container.unwire()

app = FastAPI(
    lifespan=lifespan,
    title="Simple API",
    description=(
        "API for startup project.\n\n"
    ),
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

async def exception_handler(request: Request, e: Exception) -> JSONResponse:
    error: JsonApiResponse | None = None

    if isinstance(e, RequestValidationError):
        error = ApiResponseService.format_pydantic_error(e.errors())
    elif isinstance(e, DomainException):
        error = JsonAPIService.response(errors=[e.as_dict()])
    else:
        error = JsonAPIService.error(
            status=500,
            title="Internal Server Error",
            detail=str(e),
            code=str(ErrorNo.GENERAL_ERROR.value),
            source={"traceback": traceback.format_exc()},
        )
    if error is None or error.errors is None:
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
