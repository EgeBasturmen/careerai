from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    DateTime,
    Integer,
    String,
    UniqueConstraint,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database.base import Base


class EntityEmbedding(Base):
    __tablename__ = "entity_embeddings"

    __table_args__ = (
        UniqueConstraint(
            "entity_type",
            "entity_id",
            "model_name",
            name="uq_entity_embedding_type_id_model",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    entity_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    model_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    dimension: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    source_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    source_text_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    embedding: Mapped[list[float]] = mapped_column(
        Vector(384),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )