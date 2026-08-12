from datetime import datetime
from datetime import timedelta

from sqlalchemy.orm import Session

from src.domains.jobs.repositories.job_repository import (
    JobRepository,
)
from src.domains.jobs.schemas.job_lifecycle_schema import (
    JobLifecycleResult,
)


class JobLifecycleService:
    DEFAULT_STALE_DAYS = 30

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.repository = JobRepository(db)

    def deactivate_stale_jobs(
        self,
        stale_days: int = DEFAULT_STALE_DAYS,
    ) -> JobLifecycleResult:
        if stale_days <= 0:
            raise ValueError(
                "stale_days must be greater than zero"
            )

        stale_before = (
            datetime.utcnow()
            - timedelta(days=stale_days)
        )

        deactivated_count = (
            self.repository
            .deactivate_stale_jobs(
                stale_before=stale_before,
            )
        )

        return JobLifecycleResult(
            stale_days=stale_days,
            deactivated_count=(
                deactivated_count
            ),
        )