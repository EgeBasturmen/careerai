import src.core.database.models  # noqa: F401

from src.core.database.session import SessionLocal
from src.domains.jobs.repositories.job_ingestion_run_repository import (
    JobIngestionRunRepository,
)
from src.domains.jobs.services.job_ingestion_service import (
    JobIngestionService,
)
from src.infrastructure.job_sources.fake_job_source import (
    FakeJobSource,
)
from src.infrastructure.queue.celery_app import celery_app


@celery_app.task(
    bind=True,
    name="jobs.ingest_fake_jobs",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={
        "max_retries": 3,
    },
)
def ingest_fake_jobs_task(
    self,
    run_id: int,
) -> dict:
    db = SessionLocal()

    run_repository = JobIngestionRunRepository(db)

    try:
        ingestion_run = run_repository.get_by_id(
            run_id,
        )

        if ingestion_run is None:
            raise ValueError(
                f"Job ingestion run not found: {run_id}"
            )

        run_repository.mark_started(
            ingestion_run,
        )

        service = JobIngestionService(db)

        result = service.ingest(
            source_client=FakeJobSource(),
        )

        run_repository.mark_success(
            run=ingestion_run,
            fetched_count=result.fetched_count,
            created_count=result.created_count,
            updated_count=result.updated_count,
            failed_count=result.failed_count,
            embedding_created_count=(
                result.embedding_created_count
            ),
            embedding_updated_count=(
                result.embedding_updated_count
            ),
            embedding_skipped_count=(
                result.embedding_skipped_count
            ),
            errors=result.errors,
        )

        return result.model_dump()

    except Exception as exc:
        db.rollback()

        ingestion_run = run_repository.get_by_id(
            run_id,
        )

        if ingestion_run is not None:
            run_repository.mark_failure(
                run=ingestion_run,
                error_message=(
                    f"{type(exc).__name__}: {exc}"
                ),
            )

        raise

    finally:
        db.close()