

from src.core.dto.dto import DTO
from src.core.dto.validator.jwt_token import JWTToken


class ConfirmUserRequest(DTO):
    token: JWTToken
