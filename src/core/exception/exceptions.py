import inspect
import traceback
from typing import Any

from src.core.exception.error_no import ErrorNo


class DomainException(Exception):
    def __init__(self, error_no: ErrorNo, message: str, inner_exception: Exception | None = None):
        self.errorNo = error_no.value
        self.inner_exception = inner_exception
        self.traceback = traceback.format_exc() if inner_exception else None
        self.tracestack = None
        stack = inspect.stack()
        if len(stack) > 1:
            frame = stack[1]
            self.tracestack = f"Error in function '{frame.function}': {frame.code_context[0].strip() if frame.code_context else None}, file '{frame.filename}' at line '{frame.lineno}"
        full_message = message
        if inner_exception:
            full_message += f" → {str(inner_exception)}"
        self.message = full_message
        super().__init__(full_message)

    def type(self) -> str:
        return "domain"

    def code(self) -> int:
        return 422

    def as_dict(self) -> dict[str, Any]:
        r = {
            "status": self.code(),
            "title":  self.type(),
            "detail": self.message,
            "code": self.errorNo,
            "source": {"traceback":self.traceback},
        }

        return r


class NotFoundException(DomainException):
    def type(self) -> str:
        return "not found"

    def code(self) -> int:
        return 404


class FailureException(DomainException):
    def type(self) -> str:
        return "failure"

    def code(self) -> int:
        return 422


class FailedException(DomainException):
    def type(self) -> str:
        return "failed"

    def code(self) -> int:
        return 422

class UnauthorizedException(DomainException):
    def type(self) -> str:
        return "unauthorized"

    def code(self) -> int:
        return 401

class UnprocessableEntityException(DomainException):
    def type(self) -> str:
        return "unprocessable"

    def code(self) -> int:
        return 422

class ForbiddenException(DomainException):
    def type(self) -> str:
        return "forbidden"

    def code(self) -> int:
        return 403