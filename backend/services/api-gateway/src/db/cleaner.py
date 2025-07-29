import asyncio
from datetime import UTC, datetime, timedelta

from loguru import logger
from src.db.dao import DaoFileMeta
from src.db.session import session_manager
from src.services.files import FileProcessor


class DBCleaner:
    @classmethod
    async def run(cls, older_than_minutes: int = 10):
        logger.info("[DBCleaner] 🔍 Начинаем очистку неиндексированных файлов...")

        async with session_manager.session() as session:
            threshold = datetime.now(UTC).replace(tzinfo=None) - timedelta(
                minutes=older_than_minutes
            )
            old_unindexed_files = await DaoFileMeta.get_old_unindexed_files(
                session=session, older_than=threshold
            )

            if not old_unindexed_files:
                logger.info("[DBCleaner] 🧼 Нет файлов для удаления.")
                return

            for file_meta in old_unindexed_files:
                logger.warning(
                    f"[DBCleaner] 🗑 Удаляю: {file_meta.id} ({file_meta.filename})"
                )
                await FileProcessor.delete(
                    user_id=file_meta.user_id,
                    session=session,
                    file_id=file_meta.id,
                )

            logger.info(f"[DBCleaner] ✅ Удалено файлов: {len(old_unindexed_files)}")

    @classmethod
    async def wipe_all(cls):
        """Удаляет ВСЕ файлы из базы и из S3. Только для разработки и отладки."""
        logger.warning("[DBCleaner] ⚠️ ВНИМАНИЕ: Полная очистка базы и хранилища!")

        async with session_manager.session() as session:
            all_files = await DaoFileMeta.list_all_files(session=session)
            for file_meta in all_files:
                logger.warning(f"[DBCleaner] 🔥 Удаляю ВСЁ: {file_meta.id}")
                await FileProcessor.delete(
                    user_id=file_meta.user_id,
                    session=session,
                    file_id=file_meta.id,
                )

            logger.info(
                f"[DBCleaner] 💥 Очистка завершена. Удалено файлов: {len(all_files)}"
            )


if __name__ == "__main__":
    asyncio.run(session_manager.init_db())
    asyncio.run(DBCleaner.run())
