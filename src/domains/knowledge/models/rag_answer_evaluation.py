from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from src.core.database.base import Base
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.domains.knowledge.models.rag_run import (
        RAGRun,
    )

class RAGAnswerEvaluation(Base):
    __tablename__ = "rag_answer_evaluations"

    __table_args__ = (
        Index(
            "ix_rag_answer_evaluations_rag_run_id",
            "rag_run_id",
        ),
        Index(
            "ix_rag_answer_evaluations_created_at",
            "created_at",
        ),
        Index(
            "ix_rag_answer_evaluations_passed",
            "passed",
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
    )

    overall_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    passed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    evaluator_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    failed_evaluator_names: Mapped[
        list[str]
    ] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    results: Mapped[
        list[dict[str, Any]]
    ] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    evaluation_profile: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="default",
    )

    evaluator_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="v1",
    )

    judge_provider: Mapped[
        str | None
    ] = mapped_column(
        String(100),
        nullable=True,
    )

    judge_model: Mapped[
        str | None
    ] = mapped_column(
        String(150),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    rag_run: Mapped["RAGRun"] = relationship(
        back_populates="answer_evaluations",
    )