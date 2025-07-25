from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.app.user.data.user_status import UserStatus
from src.core.db.decorator.int_enum import IntEnum
from src.core.db.entity import Entity


class User(Entity):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,)
    first_name: Mapped[str] = mapped_column(String(70), nullable=False)
    second_name: Mapped[str] = mapped_column(String(70), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    status: Mapped[UserStatus] = mapped_column(IntEnum(UserStatus), nullable=False, default=UserStatus.PENDING)
    hash_password: Mapped[str] = mapped_column(String(150), nullable=False)
    session: Mapped[str] = mapped_column(String(50), nullable=True)
    roles: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
