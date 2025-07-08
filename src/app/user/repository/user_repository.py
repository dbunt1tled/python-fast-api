

from src.app.user.model.user import User
from src.core.db.asmysql import MyDatabaseConfig
from src.core.db.repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db_config: MyDatabaseConfig):
        super().__init__(db_config, User, "id")
