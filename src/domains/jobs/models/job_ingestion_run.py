from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database.base import Base


class JobIngestionRun(Base):
    __tablename__ = "job_ingestion_runs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    task_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    fetched_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    created_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    updated_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    failed_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    errors: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    embedding_created_count = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    embedding_updated_count = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    embedding_skipped_count = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )