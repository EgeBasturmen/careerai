from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import (
    DateTime,
    String,
    Text,
    UniqueConstraint,
    Boolean,

)
from src.core.database.base import Base


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint(
            "fingerprint",
            name="uq_jobs_fingerprint",
        ),
    )
    

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    company_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    remote_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    seniority: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    required_skills: Mapped[list[str] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    source_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    external_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    normalized_title: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    normalized_company_name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    normalized_location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    fingerprint: Mapped[str] = mapped_column(
        String(64),
        nullable=True,
        unique=True,
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        index=True,
    )

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    deactivated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )