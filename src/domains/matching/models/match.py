from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey,UniqueConstraint,String,Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from src.core.database.base import Base


class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (
        UniqueConstraint(
            "resume_id",
            "job_id",
            name="uq_match_resume_job",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id"),
        nullable=False,
        index=True,
    )

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id"),
        nullable=False,
        index=True,
    )

    match_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    score_breakdown: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    matched_skills: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
    )

    missing_skills: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    algorithm_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="hybrid-v1",
        index=True,
    )

    ml_predicted_relevance: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    ml_predicted_grade: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    ml_model_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    ml_model_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    ml_feature_set_identifier: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    ml_prediction_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    ml_prediction_error: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )