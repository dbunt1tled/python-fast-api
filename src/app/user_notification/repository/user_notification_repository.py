from src.app.user.model.user import User
from src.app.user_notification.model.user_notification import UserNotification
from src.core.db.asmysql import MyDatabaseConfig
from src.core.db.repository import BaseRepository


class UserNotificationRepository(BaseRepository[UserNotification]):
    def __init__(self, db_config: MyDatabaseConfig):
        super().__init__(db_config, UserNotification, "id")
