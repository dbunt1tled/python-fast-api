from pydantic import Field

from src.core.dto.dto import DTO


class LoginRequest(DTO):
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
