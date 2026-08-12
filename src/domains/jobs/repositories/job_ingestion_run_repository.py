from datetime import datetime

from sqlalchemy.orm import Session

from src.domains.jobs.models.job_ingestion_run import (
    JobIngestionRun,
)
from src.shared.enums.job_ingestion_status import (
    JobIngestionStatus,
)


class JobIngestionRunRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        task_id: str,
        source: str,
    ) -> JobIngestionRun:
        run = JobIngestionRun(
            task_id=task_id,
            source=source,
            status=JobIngestionStatus.QUEUED.value,
        )

        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        return run

    def get_by_id(
        self,
        run_id: int,
    ) -> JobIngestionRun | None:
        return (
            self.db.query(JobIngestionRun)
            .filter(JobIngestionRun.id == run_id)
            .first()
        )

    def get_by_task_id(
        self,
        task_id: str,
    ) -> JobIngestionRun | None:
        return (
            self.db.query(JobIngestionRun)
            .filter(JobIngestionRun.task_id == task_id)
            .first()
        )

    def mark_started(
        self,
        run: JobIngestionRun,
    ) -> JobIngestionRun:
        run.status = JobIngestionStatus.STARTED.value
        run.started_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(run)

        return run

    def mark_success(
        self,
        run: JobIngestionRun,
        fetched_count: int,
        created_count: int,
        updated_count: int,
        failed_count: int,
        embedding_created_count,
        embedding_updated_count,
        embedding_skipped_count,
        errors: list[str],
    ) -> JobIngestionRun:
        run.status = JobIngestionStatus.SUCCESS.value
        run.fetched_count = fetched_count
        run.created_count = created_count
        run.updated_count = updated_count
        run.failed_count = failed_count
        run.embedding_created_count = (
            embedding_created_count
        )

        run.embedding_updated_count = (
            embedding_updated_count
        )

        run.embedding_skipped_count = (
            embedding_skipped_count
        )
        run.errors = errors
        run.completed_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(run)

        return run

    def mark_failure(
        self,
        run: JobIngestionRun,
        error_message: str,
    ) -> JobIngestionRun:
        run.status = JobIngestionStatus.FAILURE.value
        run.errors = [error_message]
        run.completed_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(run)

        return run

    def list_runs(
        self,
        source: str | None = None,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[JobIngestionRun]:
        query = self.db.query(JobIngestionRun)

        if source:
            query = query.filter(
                JobIngestionRun.source == source,
            )

        if status:
            query = query.filter(
                JobIngestionRun.status == status,
            )

        return (
            query
            .order_by(JobIngestionRun.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )