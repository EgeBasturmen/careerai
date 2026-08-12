from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from src.core.database.base import Base

if TYPE_CHECKING:
    from src.domains.knowledge.models.rag_answer_evaluation import (
        RAGAnswerEvaluation,
    )
    from src.domains.knowledge.models.rag_run_chunk import (
        RAGRunChunk,
    )


class RAGRun(Base):
    __tablename__ = "rag_runs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    answer: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    language: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        index=True,
    )

    generation_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PROCESSING",
        index=True,
    )

    sufficient_context: Mapped[bool | None] = (
        mapped_column(
            nullable=True,
        )
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    retrieval_limit: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    minimum_similarity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    candidate_result_count: Mapped[int] = (
        mapped_column(
            Integer,
            nullable=False,
            default=0,
        )
    )

    retrieval_result_count: Mapped[int] = (
        mapped_column(
            Integer,
            nullable=False,
            default=0,
        )
    )

    retriever_name: Mapped[str | None] = (
        mapped_column(
            String(100),
            nullable=True,
            index=True,
        )
    )

    reranker_name: Mapped[str | None] = (
        mapped_column(
            String(100),
            nullable=True,
            index=True,
        )
    )

    reranker_model_name: Mapped[str | None] = (
        mapped_column(
            String(255),
            nullable=True,
            index=True,
        )
    )

    context_source_count: Mapped[int] = (
        mapped_column(
            Integer,
            nullable=False,
            default=0,
        )
    )

    context_character_count: Mapped[int] = (
        mapped_column(
            Integer,
            nullable=False,
            default=0,
        )
    )

    embedding_provider: Mapped[str | None] = (
        mapped_column(
            String(100),
            nullable=True,
        )
    )

    rewrite_provider: Mapped[str | None] = (
        mapped_column(
            String(100),
            nullable=True,
        )
    )

    rewrite_model_name: Mapped[str | None] = (
        mapped_column(
            String(255),
            nullable=True,
            index=True,
        )
    )

    original_query: Mapped[str | None] = (
        mapped_column(
            Text,
            nullable=True,
        )
    )

    rewritten_query: Mapped[str | None] = (
        mapped_column(
            Text,
            nullable=True,
        )
    )

    was_rewritten: Mapped[bool] = (
        mapped_column(
            nullable=False,
            default=False,
        )
    )

    rewrite_latency_ms: Mapped[float | None] = (
        mapped_column(
            Float,
            nullable=True,
        )
    )

    rewrite_fallback_used: Mapped[bool] = (
        mapped_column(
            nullable=False,
            default=False,
        )
    )

    rewrite_fallback_reason: Mapped[str | None] = (
        mapped_column(
            Text,
            nullable=True,
        )
    )

    embedding_model_name: Mapped[str | None] = (
        mapped_column(
            String(255),
            nullable=True,
            index=True,
        )
    )

    llm_provider: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    llm_model_name: Mapped[str | None] = (
        mapped_column(
            String(255),
            nullable=True,
            index=True,
        )
    )

    prompt_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="knowledge-rag-answer",
    )

    prompt_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="v2",
    )

    retrieval_latency_ms: Mapped[float | None] = (
        mapped_column(
            Float,
            nullable=True,
        )
    )

    cache_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    cache_hit: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    cache_provider: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    cache_read_latency_ms: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    cache_write_latency_ms: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    context_build_latency_ms: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    prompt_build_latency_ms: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    llm_latency_ms: Mapped[float | None] = (
        mapped_column(
            Float,
            nullable=True,
        )
    )

    total_latency_ms: Mapped[float | None] = (
        mapped_column(
            Float,
            nullable=True,
            index=True,
        )
    )

    prompt_tokens: Mapped[int | None] = (
        mapped_column(
            Integer,
            nullable=True,
        )
    )

    completion_tokens: Mapped[int | None] = (
        mapped_column(
            Integer,
            nullable=True,
        )
    )

    total_tokens: Mapped[int | None] = (
        mapped_column(
            Integer,
            nullable=True,
        )
    )

    citations: Mapped[list[dict[str, Any]]] = (
        mapped_column(
            JSONB,
            nullable=False,
            default=list,
        )
    )

    validation_errors: Mapped[list[str]] = (
        mapped_column(
            JSONB,
            nullable=False,
            default=list,
        )
    )

    error_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    error_message: Mapped[str | None] = (
        mapped_column(
            Text,
            nullable=True,
        )
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    completed_at: Mapped[datetime | None] = (
        mapped_column(
            DateTime,
            nullable=True,
        )
    )

    chunks: Mapped[list["RAGRunChunk"]] = (
        relationship(
            back_populates="rag_run",
            cascade="all, delete-orphan",
            passive_deletes=True,
        )
    )

    answer_evaluations: Mapped[
        list["RAGAnswerEvaluation"]
    ] = relationship(
        back_populates="rag_run",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )