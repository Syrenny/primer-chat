from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import DBChunk, history_file_association
from src.db.wrap import transactional
from shared_models.indexation.core import IndexedChunk


class DaoChunks:
    @classmethod
    @transactional
    async def list_chunks(
        cls, session: AsyncSession, user_id: UUID, file_id: UUID
    ) -> list[DBChunk]:
        stmt = sa.select(DBChunk).where(
            DBChunk.user_id == user_id,
            DBChunk.file_id == file_id,
        )
        res = await session.execute(stmt)
        return res.scalars().all()

    @classmethod
    @transactional
    async def save_file_chunks(
        cls,
        session: AsyncSession,
        user_id: UUID,
        file_id: UUID,
        filename: str,
        chunks: list[IndexedChunk],
    ) -> None:
        objs = []
        for ch in chunks:
            first_page = min((p.page for p in ch.positions), default=None)
            last_page = max((p.page for p in ch.positions), default=None)
            objs.append(
                DBChunk(
                    user_id=user_id,
                    file_id=file_id,
                    filename=filename,
                    content=ch.content,
                    embedding=ch.embedding,
                    positions=[pos.model_dump() for pos in ch.positions],
                    level=ch.level,
                    title=ch.title,
                    local_summary=ch.local_summary,
                    keyphrases=ch.keyphrases or [],
                    html_tag=getattr(ch, "html_tag", None),
                    start_line=ch.start_line,
                    end_line=ch.end_line,
                    page_start=first_page,
                    page_end=last_page,
                )
            )
        session.add_all(objs)

    @classmethod
    @transactional
    async def find_history_chunks(
        cls,
        session: AsyncSession,
        user_id: UUID,
        history_id: UUID,
        query_embedding: list[float],
        limit: int,
        ivfflat_probes: int | None = 20,
    ) -> list[DBChunk]:
        """Vector-only поиск среди файлов, привязанных к истории."""

        # Настроим probes для ivfflat (увеличивает recall)
        if ivfflat_probes is not None:
            await session.execute(
                sa.text(f"SET LOCAL ivfflat.probes = {int(ivfflat_probes)}")
            )

        exists_q = (
            sa.select(sa.literal(1))
            .select_from(history_file_association)
            .where(
                history_file_association.c.history_id == history_id,
                history_file_association.c.file_id == DBChunk.file_id,
            )
        )

        dist = DBChunk.embedding.cosine_distance(query_embedding)

        stmt = (
            sa.select(DBChunk)
            .where(DBChunk.user_id == user_id, sa.exists(exists_q).correlate(DBChunk))
            .order_by(dist.asc())
            .limit(limit)
        )

        res = await session.execute(stmt)
        return res.scalars().all()

    @classmethod
    @transactional
    async def delete_file_chunks(
        cls, session: AsyncSession, user_id: UUID, file_id: UUID
    ) -> None:
        await session.execute(
            sa.delete(DBChunk).filter_by(user_id=user_id, file_id=file_id)
        )

    @classmethod
    @transactional
    async def get_chunks_by_ids(
        cls, session: AsyncSession, user_id: UUID, chunk_ids: list[UUID]
    ) -> list[DBChunk]:
        if not chunk_ids:
            return []
        res = await session.execute(
            sa.select(DBChunk).where(
                DBChunk.user_id == user_id, DBChunk.id.in_(chunk_ids)
            )
        )
        return res.scalars().all()
