from sqlalchemy import JSON, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.app.user.data.user_status import UserStatus
from src.app.user_notification.data.user_notification_status import UserNotificationStatus
from src.core.db.decorator.int_enum import IntEnum
from src.core.db.entity import Entity


class UserNotification(Entity):
    __tablename__ = "user_notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,)
    user_id: Mapped[int] = mapped_column( Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[UserNotificationStatus] = mapped_column(IntEnum(UserNotificationStatus), nullable=False, default=UserStatus.PENDING, index=True)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )
