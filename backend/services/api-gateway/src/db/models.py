import uuid
from datetime import UTC, datetime

import sqlalchemy as db
from pgvector.sqlalchemy import Vector
from shared_config import config
from shared_models.user.persona import UserPersona
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


def utcnow():
    return datetime.now(UTC)


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
        db.ForeignKey("file_meta.id"),
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
        db.DateTime(timezone=True),
        nullable=False,
        default=utcnow,
    )

    # Cookie
    cookie = relationship(
        "DBUserCookie", back_populates="user", uselist=False, lazy="selectin"
    )

    # Files
    files = relationship(
        "DBFileMeta",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Histories
    histories = relationship(
        "DBHistoryMeta",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class DBUserCookie(Base):
    __tablename__ = "cookies"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    created_at: datetime = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utcnow,
    )

    # User
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    user = relationship("DBUser", back_populates="cookie", lazy="selectin")


class DBFileMeta(Base):
    __tablename__ = "file_meta"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = db.Column(db.String, nullable=False)
    is_indexed = db.Column(db.Boolean, default=False, nullable=False)

    created_at: datetime = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utcnow,
    )

    # User
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    user = relationship("DBUser", back_populates="files", lazy="selectin")

    # Chunks
    chunks = relationship(
        "DBChunk",
        back_populates="file",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class DBMessage(Base):
    __tablename__ = "messages"

    id: uuid.UUID = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_user_message: bool = db.Column(db.Boolean, nullable=False)
    content: str = db.Column(db.Text, nullable=False)
    timestamp: datetime = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utcnow,
    )

    # History
    history_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("history_meta.id"), nullable=False
    )
    history_meta = relationship(
        "DBHistoryMeta", back_populates="messages", lazy="selectin"
    )

    # User
    user_id: uuid.UUID = db.Column(
        UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False
    )


class DBChunk(Base):
    __tablename__ = "chunks"

    id: uuid.UUID = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content: str = db.Column(db.Text, nullable=False)
    embedding = db.Column(Vector(config.embeddings.dimensions))
    html_tag = db.Column(db.String, nullable=False)
    xyxy = db.Column(ARRAY(db.Float), nullable=False)
    start_line = db.Column(db.Integer, nullable=False)
    end_line = db.Column(db.Integer, nullable=False)
    created_at: datetime = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utcnow,
    )

    # User
    user_id: uuid.UUID = db.Column(
        UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False
    )

    # File
    file_id: uuid.UUID = db.Column(
        UUID(as_uuid=True), db.ForeignKey("file_meta.id"), nullable=False
    )
    file = relationship("DBFileMeta", back_populates="chunks", lazy="selectin")


class DBHistoryMeta(Base):
    __tablename__ = "history_meta"

    id: uuid.UUID = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    summary: str = db.Column(db.Text, nullable=True)
    summary_index: int = db.Column(db.Integer, nullable=True)

    # User
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    user = relationship("DBUser", back_populates="histories", lazy="selectin")

    # Messages
    messages = relationship(
        "DBMessage",
        back_populates="history_meta",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Files
    files = relationship(
        "DBFileMeta",
        secondary=history_file_association,
        lazy="selectin",
    )
