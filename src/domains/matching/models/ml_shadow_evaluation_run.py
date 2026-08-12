from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database.base import Base


class MLShadowEvaluationRun(Base):
    __tablename__ = "ml_shadow_evaluation_runs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id"),
        nullable=False,
        index=True,
    )

    algorithm_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    ml_model_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    ml_model_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    ml_feature_set_identifier: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True,
    )

    total_match_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    shadow_prediction_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    feedback_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    successful_prediction_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    failed_prediction_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    model_not_found_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    disabled_prediction_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    mean_absolute_difference: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    grade_agreement_rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    hybrid_feedback_mae: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    ml_feedback_mae: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    recommendation: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    comparisons: Mapped[list[dict]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )