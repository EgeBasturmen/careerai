from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database.base import Base


class MatchingEvaluationRun(Base):
    __tablename__ = "matching_evaluation_runs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    dataset_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    dataset_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    algorithm_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    case_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    mean_precision_at_5: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    mean_recall_at_5: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    mean_reciprocal_rank: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    mean_ndcg_at_5: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    configuration: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    case_results: Mapped[list[dict]] = mapped_column(
        JSONB,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )