import contextlib
from collections.abc import AsyncIterator

import sqlalchemy as db
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from src.config import secrets
from src.db.dao.token import DaoToken
from src.db.dao.user import DaoUser

from .models import Base


class NotInitializedError(Exception):
    """Raised when database session manager is used before initialization."""


# Reference: https://dev.to/akarshan/asynchronous-database-sessions-in-fastapi-with-sqlalchemy-1o7e
class DatabaseSessionManager:
    def __init__(self):
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

    async def init_db(self, url: str) -> None:
        self._engine = create_async_engine(
            url,
            pool_pre_ping=True,
        )
        self._sessionmaker = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

        await self.__create_schema()

        await self.__create_default_user()

    async def __create_schema(self):
        async with self.engine.connect() as conn:
            conn = await conn.execution_options(isolation_level="AUTOCOMMIT")
            await conn.execute(db.text("CREATE EXTENSION IF NOT EXISTS vector"))
            await conn.run_sync(Base.metadata.create_all)
            await conn.execute(
                db.text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='chunks' AND column_name='embedding'
                    ) THEN
                        ALTER TABLE chunks ADD COLUMN embedding vector(768);
                    END IF;
                END$$;
            """)
            )

            # Create index if it doesn't exist
            await conn.execute(
                db.text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_indexes
                        WHERE tablename = 'chunks' AND indexname = 'chunks_embedding_idx'
                    ) THEN
                        CREATE INDEX chunks_embedding_idx
                        ON chunks USING ivfflat (embedding vector_cosine_ops)
                        WITH (lists = 100);
                    END IF;
                END$$;
            """)
            )

            # Analyze table
            await conn.execute(db.text("ANALYZE chunks"))

    async def __create_default_user(self):
        user_model = UserModel(
            email=secrets.default_admin_email.get_secret_value(),
            password=secrets.default_admin_password.get_secret_value(),
        )
        async with self.sessionmaker() as session:
            user = await DaoUser.get_user_by_email(
                session, email=secrets.default_admin_email.get_secret_value()
            )
            if user is None:
                db_user = await DaoUser.create_user(
                    session,
                    email=user_model.email,
                    password=hash_password(user_model.password),
                )
                await session.flush()
                token = generate_access_token(db_user)
                await DaoToken.create_token(
                    session=session, user_id=db_user.id, token=token
                )
                await session.commit()

    async def close(self):
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
            await session.rollback()
            raise e
        finally:
            await session.close()


session_manager = DatabaseSessionManager()


async def get_db() -> AsyncIterator[AsyncSession]:
    async with session_manager.session() as session:
        yield session
