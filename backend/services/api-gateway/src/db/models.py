import uuid
from datetime import UTC, datetime

import sqlalchemy as db
from pgvector.sqlalchemy import Vector
from shared_config import config
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    __abstract__ = True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={getattr(self, 'id', None)}>"


history_file_association = db.Table(
    "history_file_association",
    Base.metadata,
    db.Column(
        "history_id",
        UUID(as_uuid=True),
        db.ForeignKey("history_meta.id"),
        primary_key=True,
    ),
    db.Column(
        "file_id",
        UUID(as_uuid=True),
        db.ForeignKey("file_meta.id"),
        primary_key=True,
    ),
)

request_chunk_association = db.Table(
    "request_chunk_association",
    Base.metadata,
    db.Column(
        "request_id",
        UUID(as_uuid=True),
        db.ForeignKey("generation_requests.id"),
        primary_key=True,
    ),
    db.Column(
        "chunk_id",
        UUID(as_uuid=True),
        db.ForeignKey("chunks.id"),
        primary_key=True,
    ),
)


class DBUser(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    persona: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), default=utcnow
    )

    # Cookie
    cookie: Mapped["DBCookie"] = relationship(
        "DBCookie",
        lazy="selectin",
        uselist=False,
    )

    # Files
    files: Mapped[list["DBFileMeta"]] = relationship(
        "DBFileMeta",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Histories
    histories: Mapped[list["DBHistoryMeta"]] = relationship(
        "DBHistoryMeta",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class DBCookie(Base):
    __tablename__ = "cookies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), default=utcnow
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False
    )


class DBFileMeta(Base):
    __tablename__ = "file_meta"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    filename: Mapped[str] = mapped_column(db.String, nullable=False)
    is_indexed: Mapped[bool] = mapped_column(default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), default=utcnow
    )

    # User
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False
    )

    # Chunks
    chunks: Mapped[list["DBChunk"]] = relationship(
        "DBChunk",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class DBGenerationRequest(Base):
    __tablename__ = "generation_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    timestamp: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), default=utcnow
    )
    user_message: Mapped[str] = mapped_column(db.Text, nullable=False)

    assistant_message: Mapped[str | None] = mapped_column(db.Text, nullable=True)

    # History
    history_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), db.ForeignKey("history_meta.id"), nullable=False
    )

    # User
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False
    )

    retrieved_chunks: Mapped[list["DBChunk"]] = relationship(
        secondary=request_chunk_association,
        lazy="selectin",
    )


class DBChunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    content: Mapped[str] = mapped_column(db.Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(config.embeddings.dimensions))
    html_tag: Mapped[str] = mapped_column(db.String, nullable=False)
    positions: Mapped[list[dict]] = mapped_column(
        JSONB, nullable=False, comment="List[PdfLinePosition]"
    )
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), default=utcnow
    )

    # User
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False
    )

    # File
    filename: Mapped[str] = mapped_column(db.Text, nullable=False)
    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), db.ForeignKey("file_meta.id"), nullable=False
    )


class DBHistoryMeta(Base):
    __tablename__ = "history_meta"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    summary: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # User
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False
    )

    # Generation requests
    requests: Mapped[list["DBGenerationRequest"]] = relationship(
        cascade="all, delete-orphan", lazy="selectin"
    )

    # Files
    files: Mapped[list["DBFileMeta"]] = relationship(
        secondary=history_file_association,
        lazy="selectin",
    )
