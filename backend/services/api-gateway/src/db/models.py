import uuid
from datetime import UTC, datetime

import sqlalchemy as db
from pgvector.sqlalchemy import Vector
from shared_config import config
from shared_models.user.persona import UserPersona
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    __abstract__ = True


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
        db.ForeignKey("file_meta.file_id"),
        primary_key=True,
    ),
)


class DBUser(Base):
    __tablename__ = "users"

    id: uuid.UUID = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    persona = db.Column(
        JSONB, nullable=False, default=lambda: UserPersona().model_dump()
    )

    created_at: datetime = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(UTC).replace(tzinfo=None),
    )

    cookie = relationship(
        "DBUserCookie", back_populates="user", uselist=False, lazy="selectin"
    )
    files_meta = relationship(
        "DBFileMeta",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    histories = relationship(
        "DBHistoryMeta",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    chunks = relationship(
        "DBChunk", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    messages = relationship(
        "DBMessage",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class DBUserCookie(Base):
    __tablename__ = "cookies"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)

    created_at: datetime = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(UTC).replace(tzinfo=None),
    )

    user = relationship("DBUser", back_populates="cookie", lazy="selectin")


class DBFileMeta(Base):
    __tablename__ = "file_meta"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = db.Column(UUID(as_uuid=True), unique=True, nullable=False)
    filename = db.Column(db.String, nullable=False)
    is_indexed = db.Column(db.Boolean, default=False, nullable=False)

    created_at: datetime = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(UTC).replace(tzinfo=None),
    )

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)

    user = relationship("DBUser", back_populates="files_meta", lazy="selectin")
    chunks = relationship(
        "DBChunk",
        back_populates="file_meta",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    histories = relationship(
        "DBHistoryMeta",
        secondary=history_file_association,
        back_populates="files",
        lazy="selectin",
    )


# Association table for many-to-many between messages and chunks
message_chunk_association = db.Table(
    "message_chunk_association",
    Base.metadata,
    db.Column(
        "message_id", UUID(as_uuid=True), db.ForeignKey("messages.id"), primary_key=True
    ),
    db.Column(
        "chunk_id", UUID(as_uuid=True), db.ForeignKey("chunks.id"), primary_key=True
    ),
)


class DBMessage(Base):
    __tablename__ = "messages"

    id: uuid.UUID = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_user_message: bool = db.Column(db.Boolean, nullable=False)
    content: str = db.Column(db.Text, nullable=False)

    history_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("history_meta.id"), nullable=False
    )
    user_id: uuid.UUID = db.Column(
        UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False
    )

    timestamp: datetime = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(UTC).replace(tzinfo=None),
    )

    context = relationship(
        "DBChunk",
        secondary=message_chunk_association,
        back_populates="messages",
        cascade="all, delete",
    )

    history = relationship("DBHistoryMeta", back_populates="messages", lazy="selectin")

    user = relationship("DBUser", back_populates="messages")


class DBChunk(Base):
    __tablename__ = "chunks"

    id: uuid.UUID = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content: str = db.Column(db.Text, nullable=False)
    embedding = db.Column(Vector(config.embeddings.dimensions))
    html_tag = db.Column(db.String, nullable=False)
    xyxy = db.Column(ARRAY(db.Float), nullable=False)
    start_line = db.Column(db.Integer, nullable=False)
    end_line = db.Column(db.Integer, nullable=False)

    user_id: uuid.UUID = db.Column(
        UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False
    )
    file_id: uuid.UUID = db.Column(
        UUID(as_uuid=True), db.ForeignKey("file_meta.file_id"), nullable=False
    )
    created_at: datetime = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(UTC).replace(tzinfo=None),
    )

    messages = relationship(
        "DBMessage",
        secondary=message_chunk_association,
        back_populates="context",
        cascade="all, delete",
    )
    file_meta = relationship("DBFileMeta", back_populates="chunks")
    user = relationship("DBUser", back_populates="chunks")


class DBHistoryMeta(Base):
    __tablename__ = "history_meta"

    id: uuid.UUID = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    summary: str = db.Column(db.Text, nullable=True)
    summary_index: int = db.Column(db.Integer, nullable=True)

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)

    user = relationship("DBUser", back_populates="histories", lazy="selectin")
    messages = relationship(
        "DBMessage",
        back_populates="history",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    files = relationship(
        "DBFileMeta",
        secondary=history_file_association,
        back_populates="histories",
        lazy="selectin",
    )
