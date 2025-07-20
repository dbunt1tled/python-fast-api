from pydantic import Field

from src.app.user_notification.data.user_notification_status import UserNotificationStatus
from src.app.user_notification.model.user_notification import UserNotification
from src.core.dto.dto import DTO, Paginated
from src.core.http.response.response import RelationshipConfig, RelationshipType, ResponseBaseModel


class UserNotificationBase(DTO):
    message: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Message of the notification",
        examples=["Confirm your email address", "Your account has been created"],
    )


class UserNotificationCreateRequest(UserNotificationBase):

    def to_model(self) -> UserNotification:
        return UserNotification(
            data={"message": self.message}
        )

class UserNotificationListRequest(Paginated):
    status: UserNotificationStatus | None = Field(
        None,
        description="The email of the user",
        examples=["p8t2H@example.com", "Ww5rP@example.com"],
    )

class UserNotificationResponse(ResponseBaseModel):
    @property
    def model_name(self) -> str:
        return "UserNotification"

    @property
    def relationships(self) -> dict[str, RelationshipConfig]:
        return {
            "User": RelationshipConfig(
                name="User",
                service_name="user_service",
                foreign_key="id",
                relationship_type=RelationshipType.HAS_ONE
            ),
        }
