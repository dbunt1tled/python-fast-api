from datetime import datetime

from src.core.dto.dto import DTO
from src.core.service.dto.token import TokenBearer


class Bearer(DTO):
    id: int
    access_token: str
    access_token_exp: datetime
    refresh_token: str
    refresh_token_exp: datetime

    @staticmethod
    def from_token(token: TokenBearer) -> "Bearer":
        return Bearer(
            id=token.user_id,
            access_token=token.access_token.token,
            access_token_exp=token.access_token.expires_in,
            refresh_token=token.refresh_token.token,
            refresh_token_exp=token.refresh_token.expires_in,
        )
