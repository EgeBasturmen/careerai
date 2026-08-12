import src.core.database.models  # noqa: F401

from src.core.database.session import SessionLocal
from src.domains.jobs.services.job_lifecycle_service import (
    JobLifecycleService,
)
from src.infrastructure.queue.celery_app import (
    celery_app,
)


@celery_app.task(
    bind=True,
    name="jobs.deactivate_stale_jobs",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={
        "max_retries": 3,
    },
)
def deactivate_stale_jobs_task(
    self,
    stale_days: int = 30,
) -> dict:
    db = SessionLocal()

    try:
        result = (
            JobLifecycleService(db)
            .deactivate_stale_jobs(
                stale_days=stale_days,
            )
        )

        return result.model_dump()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()