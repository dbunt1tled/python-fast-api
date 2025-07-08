from pydantic import AliasGenerator, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.app.user.data.role import Role
from src.app.user.data.user_status import UserStatus


class UserBase(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        alias_generator=AliasGenerator(
            alias=to_camel,
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        populate_by_name=True
    )

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
    pass

