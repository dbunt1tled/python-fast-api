from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    CONFIRMATION = "confirmation"

class Token:
    token: str
    token_type: TokenType
    subject: str
    session: str | None
    email: str | None
    expires_in: datetime

    def __init__(
        self,
        token: str,
        token_type: TokenType,
        subject: str,
        expires_in: datetime,
        session: str | None = None,
        email: str | None = None,
    ) -> None:
        self.token = token
        self.token_type = token_type
        self.subject = subject
        self.session = session
        self.email = email
        self.expires_in = expires_in

    @staticmethod
    def from_payload(token : str, payload: dict) -> "Token":
        return Token(
            token=token,
            token_type=payload["type"],
            subject=payload["sub"],
            session=payload.get("session", None),
            email=payload.get("email", None),
            expires_in=datetime.fromtimestamp(timestamp=int(payload["exp"]), tz=timezone.utc),
        )

@dataclass
class TokenBearer:
    user_id: int
    access_token: Token
    refresh_token: Token
