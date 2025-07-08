from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    CONFIRMATION = "confirmation"

@dataclass
class Token:
    token: str
    token_type: TokenType
    expires_in: datetime

@dataclass
class TokenBearer:
    user_id: int
    access_token: Token
    refresh_token: Token
