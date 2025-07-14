from pydantic import Field

from src.app.user.data.role import Role
from src.app.user.data.user_status import UserStatus
from src.app.user.model.user import User
from src.core.dto.dto import DTO, Paginated
from src.core.http.response.response import BaseModelResponse, RelationshipConfig, RelationshipType


class UserBase(DTO):
    first_name: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="The first name of the user",
        examples=["John", "Mark"],
    )
    second_name: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="The second name of the user",
        examples=["Doe", "Smith"],
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
    status: UserStatus | None = Field(
        None,
        description="The status of the user",
        examples=[UserStatus.PENDING, UserStatus.ACTIVE, UserStatus.INACTIVE],
    )
    roles: list | None = Field(
        None,
        description="The roles of the user",
        examples=[Role.ADMIN, Role.USER],
    )



class UserCreateRequest(UserBase):

    def to_user(self) -> User:
        return User(
            first_name=self.first_name,
            second_name=self.second_name,
            email=self.email,
            status=UserStatus.PENDING,
            roles=self.roles or [Role.USER],
        )

class UserListRequest(Paginated):
    email: str | None = Field(
        None,
        min_length=3,
        max_length=255,
        description="The email of the user",
        examples=["p8t2H@example.com", "Ww5rP@example.com"],
    )

class UserResponse(BaseModelResponse):
    @property
    def model_name(self) -> str:
        return "User"

    @property
    def relationships(self) -> dict[str, RelationshipConfig]:
        return {
            "UserNotification": RelationshipConfig(
                name="UserNotification",
                service_name="user_notification_service",
                service_method="new_by_user_id",
                foreign_key="user_id",
                relationship_type=RelationshipType.HAS_MANY
            )
        }

    # relationship on by own
    # RelationshipConfig(
    #     name="User",
    #     service_name="user_service",
    #     foreign_key="id",
    #     local_key="user_id",
    #     relationship_type=RelationshipType.BELONGS_TO
    # )