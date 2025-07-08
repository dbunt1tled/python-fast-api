import base64
import jwt
from datetime import datetime, timedelta
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from src.app.user.model.user import User
from src.core.service.dto.token import Token, TokenBearer, TokenType


class HashService:
    def __init__(
            self,
            jwt_public_key: str,
            jwt_private_key: str,
            jwt_algorithm: str,
            jwt_access_token_exp_h: int,
            jwt_refresh_token_exp_h: int
    ) -> None:
        self.jwt_public_key = base64.b64decode(jwt_public_key).decode("utf-8")
        self.jwt_private_key = base64.b64decode(jwt_private_key).decode("utf-8")
        self.jwt_algorithm = jwt_algorithm
        if self.jwt_algorithm is None or self.jwt_algorithm == "":
            self.jwt_algorithm = "RS256"
        self.jwt_access_token_exp_h = jwt_access_token_exp_h
        self.jwt_refresh_token_exp_h = jwt_refresh_token_exp_h
        self.hasher = PasswordHasher()

    def hash_password(self, password: str) -> str:
        return self.hasher.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        try:
            self.hasher.verify(hashed_password, password)
            return True
        except VerifyMismatchError:
            return False

    def create_access_token(self, user: User) -> Token:
        exp = datetime.now() + timedelta(hours=self.jwt_access_token_exp_h)
        payload = {
            "sub": user.id,
            "type": TokenType.ACCESS,
            "exp": int(exp.timestamp()),
        }

        token = jwt.encode(payload, self.jwt_private_key, algorithm=self.jwt_algorithm)

        return Token(
            token=str(token),
            token_type= TokenType.ACCESS,
            expires_in=exp,
        )

    def create_refresh_token(self, user: User) -> Token:
        exp = datetime.now() + timedelta(hours=self.jwt_refresh_token_exp_h)
        payload = {
            "sub": user.id,
            "type": TokenType.REFRESH,
            "exp": int(exp.timestamp()),
        }

        token = jwt.encode(payload, self.jwt_private_key, algorithm=self.jwt_algorithm)

        return Token(
            token=str(token),
            token_type= TokenType.REFRESH,
            expires_in=exp,
        )

    def create_token_bearer(self, user: User) -> TokenBearer:
        return TokenBearer(
            user_id=user.id,
            access_token=self.create_access_token(user=user),
            refresh_token=self.create_refresh_token(user=user),
        )

    def verify_token(self, token: str, check_expiration: bool = True) -> dict | None:
        try:
            payload = jwt.decode(
                token,
                self.jwt_public_key,
                algorithms=[self.jwt_algorithm],
                options={
                    "verify_signature": True,
                    "verify_expiration": check_expiration
                }
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None