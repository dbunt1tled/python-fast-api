
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.user.models.user import User
from src.core.db.repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User, "id")
