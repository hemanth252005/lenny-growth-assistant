import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TranscriptChunk(Base):
    __tablename__ = "transcript_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    episode_title: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )

    guest_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    episode_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    timestamp: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    topic: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(384),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
