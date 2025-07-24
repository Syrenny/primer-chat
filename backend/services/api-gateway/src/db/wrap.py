from functools import wraps

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession


def transactional(func):
    @wraps(func)
    async def wrapper(*args, session: AsyncSession, **kwargs):
        try:
            result = await func(*args, session=session, **kwargs)
            await session.commit()
            return result
        except Exception as e:
            await session.rollback()
            logger.exception(f"Ошибка в транзакции: {e}")
            raise e

    return wrapper
