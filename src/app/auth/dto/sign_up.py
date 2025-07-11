from pydantic import Field

from src.app.user.data.role import Role
from src.app.user.data.user_status import UserStatus
from src.app.user.model.user import User
from src.core.dto.dto import DTO


class SignupRequest(DTO):
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
    first_name: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="The password of the user",
        examples=["John", "Mark"],
    )

    second_name: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="The password of the user",
        examples=["Smith", "Average"],
    )

    def to_user(self) -> User:
        return User(
            first_name=self.first_name,
            second_name=self.second_name,
            email=self.email,
            status=UserStatus.PENDING,
            roles=[Role.USER],
        )
