from typing import Protocol, cast
from fastapi import Request
from src.app.user.model.user import User
from src.core.exception.error_no import ErrorNo
from src.core.exception.exceptions import UnauthorizedException


class State(Protocol):
    user: User | None = None
    is_authenticated: bool = False

class AuthState(State):
    user: User

def get_state(request: Request) -> State:
    if not hasattr(request.state, "user"):
        request.state.user = None
    if not hasattr(request.state, "is_authenticated"):
        request.state.is_authenticated = False
    return cast(State, request.state)

def get_auth_state(request: Request) -> AuthState:
    if (
        not hasattr(request.state, "user")
        or request.state.user is None
        or not hasattr(request.state, "is_authenticated")
        or not request.state.is_authenticated
    ):
        raise UnauthorizedException(
            error_no=ErrorNo.AUTHORIZATION_USER_NOT_AUTHENTICATED,
            message="User is not authenticated"
        )
    return cast(AuthState, request.state)