import base64
from datetime import datetime, timedelta
import secrets
import string
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from src.app.user.model.user import User
from src.core.service.dto.token import Token, TokenBearer, TokenType
from src.core.settings.setting import Settings


class HashService:
    def __init__(
            self,
            cfg: Settings
    ) -> None:
        self.cfg = cfg
        self.jwt_public_key = base64.b64decode(cfg.jwt_public_key).decode("utf-8")
        self.jwt_private_key = base64.b64decode(cfg.jwt_private_key).decode("utf-8")
        self.jwt_algorithm = cfg.jwt_algorithm
        if self.jwt_algorithm is None or self.jwt_algorithm == "":
            self.jwt_algorithm = "RS256"
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
        exp = datetime.now() + timedelta(hours=self.cfg.jwt_access_token_exp_h)
        payload = {
            "sub": str(user.id),
            "type": TokenType.ACCESS,
            "session": user.session,
            "exp": int(exp.timestamp()),
        }

        token = jwt.encode(payload, self.jwt_private_key, algorithm=self.jwt_algorithm)

        return Token(
            subject=str(user.id),
            token=str(token),
            token_type= TokenType.ACCESS,
            expires_in=exp,
        )

    def create_refresh_token(self, user: User) -> Token:
        exp = datetime.now() + timedelta(hours=self.cfg.jwt_refresh_token_exp_h)
        payload = {
            "sub": str(user.id),
            "type": TokenType.REFRESH,
            "session": user.session,
            "exp": int(exp.timestamp()),
        }

        token = jwt.encode(payload, self.jwt_private_key, algorithm=self.jwt_algorithm)

        return Token(
            subject=str(user.id),
            token=str(token),
            token_type= TokenType.REFRESH,
            expires_in=exp,
        )

    def create_token_confirm(self, user: User) -> Token:
        exp = datetime.now() + timedelta(hours=self.cfg.jwt_confirm_token_exp_h)
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "session": user.session,
            "type": TokenType.CONFIRMATION,
            "exp": int(exp.timestamp()),
        }

        token = jwt.encode(payload, self.jwt_private_key, algorithm=self.jwt_algorithm)

        return Token(
            subject=str(user.id),
            token=str(token),
            token_type= TokenType.CONFIRMATION,
            expires_in=exp,
        )

    def create_token_bearer(self, user: User) -> TokenBearer:
        return TokenBearer(
            user_id=user.id,
            access_token=self.create_access_token(user=user),
            refresh_token=self.create_refresh_token(user=user),
        )

    def verify_token(self, token: str, check_expiration: bool = True) -> Token | None:
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
            return Token.from_payload(token=token, payload=payload)
        except jwt.ExpiredSignatureError as e:
            print(e)
            return None
        except jwt.InvalidTokenError as e:
            print(e)
            return None

    @staticmethod
    def random_string(
        length: int = 16,
        include_uppercase: bool= True,
        include_lowercase: bool= True,
        include_digits: bool= True,
        include_punctuation: bool= False,
        custom_chars: str | None = None,
    ) -> str:
        if length < 1:
            raise ValueError("Length must be at least 1")

        if custom_chars:
            chars = custom_chars
        else:
            chars = ""
            if include_uppercase:
                chars += string.ascii_uppercase
            if include_lowercase:
                chars += string.ascii_lowercase
            if include_digits:
                chars += string.digits
            if include_punctuation:
                chars += string.punctuation

            if not chars:
                raise ValueError("No characters selected for random string generation")

        return ''.join(secrets.choice(chars) for _ in range(length))