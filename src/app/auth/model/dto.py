from datetime import datetime

from pydantic import AliasGenerator, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.core.service.dto.token import TokenBearer


class LoginRequest(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        alias_generator=AliasGenerator(
            alias=to_camel,
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True
    )

    email: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="The email of the user",
        examples=["p8t2H@example.com", "Ww5rP@example.com"],
    )
    password: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="The password of the user",
        examples=["password", "password123"],
    )

class AccessApp(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        alias_generator=AliasGenerator(
            alias=to_camel,
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True,
    )
    id: int
    access_token: str
    access_token_exp: datetime
    refresh_token: str
    refresh_token_exp: datetime

    @staticmethod
    def from_token(token: TokenBearer) -> "AccessApp":
        return AccessApp(
            id=token.user_id,
            access_token=token.access_token.token,
            access_token_exp=token.access_token.expires_in,
            refresh_token=token.refresh_token.token,
            refresh_token_exp=token.refresh_token.expires_in,
        )
