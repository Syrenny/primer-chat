import uuid
from datetime import UTC, datetime

import sqlalchemy as db
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship

from server.models import Action


class Base(DeclarativeBase):
    pass


class DBUser(Base):
    __tablename__ = "users"

    id: uuid.UUID = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: str = db.Column(db.String, unique=True, nullable=False)
    password: str = db.Column(db.String, nullable=False)

    token = relationship("DBToken", back_populates="user", uselist=False)
    chunks = relationship(
        "DBChunk", back_populates="user", cascade="all, delete-orphan"
    )
    files_meta = relationship(
        "DBFileMeta", back_populates="user", cascade="all, delete-orphan"
    )
    messages = relationship(
        "DBMessage", back_populates="user", cascade="all, delete-orphan"
    )


class DBToken(Base):
    __tablename__ = "tokens"

    id: uuid.UUID = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: uuid.UUID = db.Column(
        UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False
    )
    token: str = db.Column(db.String, nullable=False, unique=True)
    created_at: datetime = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(UTC).replace(tzinfo=None),
    )

    user = relationship("DBUser", back_populates="token")


class DBFileMeta(Base):
    __tablename__ = "file_meta"

    id: uuid.UUID = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id: uuid.UUID = db.Column(
        UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4
    )
    user_id: uuid.UUID = db.Column(
        UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False
    )
    filename: str = db.Column(db.String, nullable=False)
    is_indexed: bool = db.Column(db.Boolean, nullable=False, default=False)

    user = relationship("DBUser", back_populates="files_meta")
    chunks = relationship(
        "DBChunk", back_populates="file_meta", cascade="all, delete-orphan"
    )
    messages = relationship(
        "DBMessage", back_populates="file_meta", cascade="all, delete-orphan"
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
    file_id: uuid.UUID = db.Column(
        UUID(as_uuid=True), db.ForeignKey("file_meta.file_id"), nullable=False
    )
    user_id: uuid.UUID = db.Column(
        UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False
    )
    content: str = db.Column(db.Text, nullable=False)
    action: Action = db.Column(
        db.Enum(Action, name="action_type"), nullable=False, default=None
    )
    snippet: str = db.Column(db.Text, nullable=True, default=None)
    timestamp: datetime = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(UTC).replace(tzinfo=None),
    )
    is_user_message: bool = db.Column(db.Boolean, nullable=False)

    context = relationship(
        "DBChunk",
        secondary=message_chunk_association,
        back_populates="messages",
        cascade="all, delete",
    )

    file_meta = relationship("DBFileMeta", back_populates="messages")
    user = relationship("DBUser", back_populates="messages")


class DBChunk(Base):
    __tablename__ = "chunks"

    id: uuid.UUID = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: uuid.UUID = db.Column(
        UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False
    )
    filename: str = db.Column(db.String, nullable=False)
    file_id: uuid.UUID = db.Column(
        UUID(as_uuid=True), db.ForeignKey("file_meta.file_id"), nullable=False
    )
    chunk_text: str = db.Column(db.Text, nullable=False)
    created_at: datetime = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(UTC).replace(tzinfo=None),
    )
    embedding = db.Column(Vector(1024))

    messages = relationship(
        "DBMessage",
        secondary=message_chunk_association,
        back_populates="context",
        cascade="all, delete",
    )
    file_meta = relationship("DBFileMeta", back_populates="chunks")
    user = relationship("DBUser", back_populates="chunks")
