from pydantic import Field

from src.core.dto.dto import DTO


class ReSendConfirmEmailRequest(DTO):
    email: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="The email of the user",
        examples=["p8t2H@example.com", "Ww5rP@example.com"],
    )
