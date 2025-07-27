import contextlib
from collections.abc import AsyncIterator

from alembic import command
from alembic.config import Config
from anyio import to_thread
from loguru import logger
from shared_config import secrets
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class NotInitializedError(Exception):
    """Raised when database session manager is used before initialization."""


# Reference: https://dev.to/akarshan/asynchronous-database-sessions-in-fastapi-with-sqlalchemy-1o7e
class DatabaseSessionManager:
    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker | None = None

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            raise NotInitializedError("Engine is not initialized.")
        return self._engine

    @property
    def sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        if self._sessionmaker is None:
            raise NotInitializedError("Sessionmaker is not initialized.")
        return self._sessionmaker

    async def init_db(self, run_migrations: bool = False) -> None:
        self._engine = create_async_engine(
            str(secrets.sqlalchemy_url),
            pool_pre_ping=True,
        )
        self._sessionmaker = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

        if run_migrations:
            await to_thread.run_sync(self._run_migrations)

            logger.debug("Migration end")

    def _run_migrations(self) -> None:
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", str(secrets.sqlalchemy_url))
        command.upgrade(alembic_cfg, "head")

    async def close(self) -> None:
        if self._engine is not None:
            await self.engine.dispose()
            self._engine = None
            self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        session = self.sessionmaker()
        try:
            yield session
        except Exception as e:
            logger.exception(str(e))
            await session.rollback()
            raise e
        finally:
            await session.close()


session_manager = DatabaseSessionManager()


async def get_db() -> AsyncIterator[AsyncSession]:
    async with session_manager.session() as session:
        yield session
