from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from src.core.database.base import Base

if TYPE_CHECKING:
    from src.domains.knowledge.models.rag_run import (
        RAGRun,
    )


class RAGRunChunk(Base):
    __tablename__ = "rag_run_chunks"

    __table_args__ = (
        UniqueConstraint(
            "rag_run_id",
            "source_number",
            name=(
                "uq_rag_run_chunks_"
                "run_source_number"
            ),
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    rag_run_id: Mapped[int] = mapped_column(
        ForeignKey(
            "rag_runs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    knowledge_chunk_id: Mapped[int] = (
        mapped_column(
            ForeignKey(
                "knowledge_chunks.id",
                ondelete="SET NULL",
            ),
            nullable=True,
            index=True,
        )
    )

    knowledge_document_id: Mapped[int] = (
        mapped_column(
            ForeignKey(
                "knowledge_documents.id",
                ondelete="SET NULL",
            ),
            nullable=True,
            index=True,
        )
    )

    source_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    retrieval_rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    document_title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    chunk_content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    similarity_score: Mapped[float] = (
        mapped_column(
            Float,
            nullable=False,
        )
    )

    was_included_in_context: Mapped[bool] = (
        mapped_column(
            nullable=False,
            default=True,
        )
    )

    was_cited: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    chunk_metadata: Mapped[dict[str, Any]] = (
        mapped_column(
            JSONB,
            nullable=False,
            default=dict,
        )
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    rag_run: Mapped["RAGRun"] = relationship(
        back_populates="chunks",
    )