from uuid import UUID

from loguru import logger
from shared_models.openai.completions import ChatMessage
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import config as local_config
from src.db.dao.history_meta import DaoHistoryMeta
from src.db.models import DBFileMeta
from src.exceptions.history import HistoryMetaNotFoundError
from src.models.dto.history import HistoryMeta, HistoryMetaSummary
from src.models.dto.requests import GenerationRequest
from src.services.summarization import SummaryService


class HistoryMessagesService:
    @classmethod
    async def _summarize(
        cls, messages: list[ChatMessage], summary: HistoryMetaSummary
    ) -> str:
        summary_service = SummaryService()
        previous_summary_message = ChatMessage(
            role="assistant", content=summary.content
        )
        summary_response, _ = await summary_service.summarize(
            history=[previous_summary_message]
            + messages[summary.summary_message_index :]
        )

        return summary_response.summary

    @classmethod
    async def _maybe_summarize(
        cls,
        messages: list[ChatMessage],
        summary: HistoryMetaSummary,
    ) -> HistoryMetaSummary | None:
        history_length = len(messages)
        if (
            history_length - summary.summary_message_index
            < local_config.generation.max_len_history
        ):
            return None

        summary = await cls._summarize(messages=messages, summary=summary)
        return HistoryMetaSummary(summary_message_index=history_length, summary=summary)

    @classmethod
    def _construct_openai_history(
        cls, messages: list[ChatMessage], summary: HistoryMetaSummary
    ) -> list[ChatMessage]:
        summary_message = ChatMessage(role="assistant", content=summary.content)

        return [summary_message] + messages

    @classmethod
    async def get_history_messages(
        cls, user_id: UUID, history_id: UUID, session: AsyncSession
    ) -> list[ChatMessage]:
        history_meta = await HistoryMetaService.get_history_meta(
            user_id=user_id, history_id=history_id, session=session
        )

        messages = GenerationRequest.to_chm(history_meta.requests)

        history_meta_summary = await cls._maybe_summarize(
            summary=history_meta.summary, messages=messages
        )

        if history_meta_summary:
            logger.debug(
                f"Summarization ended for history_id={history_meta.history_id}"
            )
            history_meta = await HistoryMetaService.update_history_meta(
                user_id=user_id,
                history_id=history_id,
                session=session,
                summary=history_meta_summary,
            )

        return cls._construct_openai_history(
            summary=history_meta.summary, messages=messages
        )


class HistoryMetaService:
    @classmethod
    async def get_history_meta(
        cls, user_id: UUID, history_id: UUID, session: AsyncSession
    ) -> HistoryMeta:
        db_history_meta = await DaoHistoryMeta.get_history_meta(
            session=session, user_id=user_id, history_id=history_id
        )

        if not db_history_meta:
            raise HistoryMetaNotFoundError(history_id=history_id)

        return HistoryMeta.from_orm(db_history_meta)

    @classmethod
    async def create_history_meta(
        cls,
        user_id: UUID,
        session: AsyncSession,
        db_files: list[DBFileMeta] | None = None,
    ) -> HistoryMeta:
        summary = HistoryMetaSummary()
        _db_history_meta = await DaoHistoryMeta.add_history_meta(
            session=session, user_id=user_id, summary=summary, files=db_files
        )

        return await cls.get_history_meta(
            session=session, user_id=user_id, history_id=_db_history_meta.id
        )

    @classmethod
    async def update_history_meta(
        cls,
        user_id: UUID,
        history_id: UUID,
        session: AsyncSession,
        summary: HistoryMetaSummary | None = None,
        db_files: list[DBFileMeta] | None = None,
    ) -> HistoryMeta | None:
        _db_history_meta = await DaoHistoryMeta.update_history_meta(
            session=session,
            user_id=user_id,
            history_id=history_id,
            summary=summary,
            files=db_files,
        )

        if not _db_history_meta:
            return None

        return await cls.get_history_meta(
            session=session, user_id=user_id, history_id=_db_history_meta.id
        )
