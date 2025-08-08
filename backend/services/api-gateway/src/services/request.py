from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from src.db.dao import DaoRequest
from src.db.models import DBChunk
from src.models.dto.requests import GenerationRequest


class RequestService:
    @classmethod
    async def get_request(
        cls,
        user_id: UUID,
        request_id: UUID,
        session: AsyncSession,
    ) -> GenerationRequest | None:
        db_request = await DaoRequest.get_request(
            session=session,
            user_id=user_id,
            request_id=request_id,
        )
        if not db_request:
            return None
        return GenerationRequest.from_orm(db_request)

    @classmethod
    async def create_request(
        cls,
        user_id: UUID,
        history_id: UUID,
        session: AsyncSession,
        user_message: str = None,
        assistant_message: str | None = None,
        chunks: list[DBChunk] | None = None,
    ) -> GenerationRequest:
        _db_request = await DaoRequest.add_request(
            session=session,
            user_id=user_id,
            history_id=history_id,
            chunks=chunks,
            user_message=user_message,
            assistant_message=assistant_message,
        )

        return await cls.get_request(
            request_id=_db_request.id, user_id=user_id, session=session
        )

    @classmethod
    async def update_request(
        cls,
        user_id: UUID,
        request_id: UUID,
        session: AsyncSession,
        user_message: str | None = None,
        assistant_message: str | None = None,
        chunks: list[DBChunk] | None = None,
    ) -> GenerationRequest | None:
        _db_request = await DaoRequest.update_request(
            session=session,
            user_id=user_id,
            request_id=request_id,
            chunks=chunks,
            user_message=user_message,
            assistant_message=assistant_message,
        )

        if not _db_request:
            return None

        return await cls.get_request(
            session=session, user_id=user_id, request_id=_db_request.id
        )

    @classmethod
    async def list_requests(
        cls,
        user_id: UUID,
        history_id: UUID,
        session: AsyncSession,
    ) -> list[GenerationRequest]:
        db_requests = await DaoRequest.list_requests(
            session=session, user_id=user_id, history_id=history_id
        )

        return GenerationRequest.from_orm_list(db_requests)
