from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aiomysql  # type: ignore 
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


class MyDatabaseConfig:
    conn = None

    def __init__(
        self,
        dsn: str,
    ):
        self.dsn = dsn
        self.database_url = f"{self.dsn}"

        self.engine = create_async_engine(
            self.database_url,
            echo=False,
            pool_pre_ping=True,
            poolclass=StaticPool,
            connect_args={"charset": "utf8mb4", "cursorclass": aiomysql.SSCursor},
        )

        self.async_session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def close(self) -> None:
        if self.engine is not None:
            await self.engine.dispose()