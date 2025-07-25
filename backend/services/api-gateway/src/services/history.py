from functools import lru_cache
from uuid import UUID

from shared_models.openai.completions import ChatMessage
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import config as local_config
from src.db.dao.history_meta import DaoHistoryMeta
from src.db.dao.messages import DaoMessages
from src.services.summarization import SummaryService


@lru_cache
def get_summary_service() -> SummaryService:
    return SummaryService()


class HistoryService:
    @classmethod
    async def _maybe_summarize(
        cls,
        user_id: UUID,
        history_id: UUID,
        session: AsyncSession,
        history: list[ChatMessage],
    ) -> list[ChatMessage]:
        history_meta = await DaoHistoryMeta.get_history_meta(
            session=session, user_id=user_id, history_id=history_id
        )
        history_length = len(history)
        if (
            history_length - history_meta.summary_index
            < local_config.generation.max_len_history
        ):
            return history
        summary_service = get_summary_service()

        summary_message = ChatMessage(role="assistant", content=history_meta.summary)

        summary = await summary_service.summarize(
            history=[summary_message] + history[history_meta.summary_index :]
        )

        DaoHistoryMeta.update_history_meta(
            session=session,
            user_id=user_id,
            history_id=history_id,
            summary=summary,
            summary_index=history_length,
        )

        return [summary]

    @classmethod
    async def get_history(
        cls, user_id: UUID, history_id: UUID, session: AsyncSession
    ) -> list[ChatMessage]:
        messages = DaoMessages.get_messages(
            session=session, user_id=user_id, history_id=history_id
        )
        return cls._maybe_summarize(messages)
