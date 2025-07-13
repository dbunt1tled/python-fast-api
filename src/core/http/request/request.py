from fastapi import Request
from typing import cast

class ApiRequest(Request):
    @property
    def state(self) -> StateProtocol:
        return cast(StateProtocol, super().state)