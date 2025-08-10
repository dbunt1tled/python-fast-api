import json
import re
from collections.abc import Generator
from enum import Enum
from typing import Any, TypeVar, Type

from fastapi import Request

T = TypeVar("T")

invert_case_regex = re.compile(r"(?<!^)(?=[A-Z])")


def is_enum_value(enum_class: Type[Enum], value: Any) -> bool:
    try:
        enum_class(value)
        return True
    except (ValueError, TypeError):
        return False


def is_enum_member(enum_class: Type[Enum], name: str) -> bool:
    return name in enum_class.__members__


def chunked(iterable: list[T], size: int) -> Generator[list[T]]:
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


def to_invert_case(s: str) -> str:
    s = re.sub(invert_case_regex, "_", s).lower()
    return " ".join(word.capitalize() for word in s.split("_"))


def filter_headers(request: Request) -> dict[str, str]:
    return filter_params(params=request.headers.items())


def filter_params(params: dict[str, Any] | list[tuple[str, Any]] | list[dict[str, Any]]) -> dict[str, Any]:
    params_to_remove = [
        "password",
        "passwordConfirmation",
        "x-api-key",
        "accessToken",
        "refreshToken",
    ]  # TODO improve not working
    if isinstance(params, list):
        params = {k: v for k, v in params}
    return {k: v for k, v in params.items() if k.lower() not in params_to_remove}


def extract_body(request: Request, secure: bool = False, as_dict: bool = False) -> dict[str, Any] | str:
    result: dict[str, Any] | str = {} if as_dict else ""
    if not hasattr(request.state, "body"):
        return result
    body = request.state.body
    if not body:
        return result
    body_request = body.decode("utf-8", errors="ignore")
    try:
        result = json.loads(body_request)
        if secure:
            result = filter_params(result)
        if not as_dict:
            result = json.dumps(result, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        pass

    return result
