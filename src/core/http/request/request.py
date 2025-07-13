
from fastapi import Request

from src.core.http.request.state import State, get_state


class ApiRequest(Request):

    def data(self) -> State:
        return get_state(self)
