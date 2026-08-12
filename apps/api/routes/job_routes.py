from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.core.database.session import get_db
from src.core.security.dependencies import get_current_user
from src.domains.jobs.schemas.job_schema import (
    JobCreateRequest,
    JobResponse,
)
from celery.utils import uuid

from src.domains.jobs.repositories.job_ingestion_run_repository import (
    JobIngestionRunRepository,
)
from src.domains.jobs.schemas.job_ingestion_schema import (
    JobIngestionTaskResponse,
    JobSourceIngestionRequest,
)
from src.infrastructure.queue.job_source_tasks import (
    ingest_job_source_task,
)
from src.domains.jobs.services.job_service import JobService
from src.domains.users.models.user import User
from fastapi import APIRouter, Depends, Query
from src.domains.jobs.schemas.job_ingestion_schema import (
    JobIngestionResult,
)
from src.domains.jobs.services.job_ingestion_service import (
    JobIngestionService,
)
from src.infrastructure.job_sources.fake_job_source import (
    FakeJobSource,
)
from src.domains.jobs.schemas.job_ingestion_schema import (
    JobIngestionTaskResponse,
)
from src.infrastructure.queue.job_ingestion_tasks import (
    ingest_fake_jobs_task,
)
from celery.result import AsyncResult

from src.infrastructure.queue.celery_app import celery_app
from celery.utils import uuid
from fastapi import Query

from src.domains.jobs.repositories.job_ingestion_run_repository import (
    JobIngestionRunRepository,
)
from src.domains.jobs.schemas.job_ingestion_schema import (
    JobIngestionRunResponse,
    JobIngestionTaskResponse,
)
from src.infrastructure.queue.job_ingestion_tasks import (
    ingest_fake_jobs_task,
)

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


@router.post(
    "",
    response_model=JobResponse,
)
def create_job(
    request: JobCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = JobService(db)

    return service.create_job(request)


@router.get(
    "",
    response_model=list[JobResponse],
)
def list_jobs(
    seniority: str | None = None,
    remote_type: str | None = None,
    location: str | None = None,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = JobService(db)

    return service.list_jobs(
        seniority=seniority,
        remote_type=remote_type,
        location=location,
        limit=limit,
        offset=offset,
    )

@router.get(
    "/{job_id}",
    response_model=JobResponse,
)
def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = JobService(db)

    return service.get_job(
        job_id=job_id,
    )


@router.post(
    "/ingestion/fake/async",
    response_model=JobIngestionTaskResponse,
    status_code=202,
)
def enqueue_fake_job_ingestion(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task_id = uuid()

    run_repository = JobIngestionRunRepository(db)

    ingestion_run = run_repository.create(
        task_id=task_id,
        source="fake",
    )

    try:
        ingest_fake_jobs_task.apply_async(
            kwargs={
                "run_id": ingestion_run.id,
            },
            task_id=task_id,
        )

    except Exception:
        db.rollback()

        run_repository.mark_failure(
            run=ingestion_run,
            error_message="Task could not be queued",
        )

        raise

    return JobIngestionTaskResponse(
        run_id=ingestion_run.id,
        task_id=task_id,
        status=ingestion_run.status,
        source=ingestion_run.source,
    )
@router.get(
    "/ingestion/runs",
    response_model=list[JobIngestionRunResponse],
)
def list_job_ingestion_runs(
    source: str | None = None,
    run_status: str | None = Query(
        default=None,
        alias="status",
        pattern="^(QUEUED|STARTED|SUCCESS|FAILURE)$",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repository = JobIngestionRunRepository(db)

    runs = repository.list_runs(
        source=source,
        status=run_status,
        limit=limit,
        offset=offset,
    )

    return [
        JobIngestionRunResponse.model_validate(run)
        for run in runs
    ]

@router.get(
    "/ingestion/runs/{run_id}",
    response_model=JobIngestionRunResponse,
)
def get_job_ingestion_run(
    run_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repository = JobIngestionRunRepository(db)

    ingestion_run = repository.get_by_id(
        run_id,
    )

    if ingestion_run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job ingestion run not found",
        )

    return JobIngestionRunResponse.model_validate(
        ingestion_run,
    )

@router.get(
    "/ingestion/tasks/{task_id}",
)
def get_job_ingestion_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
):
    task_result = AsyncResult(
        task_id,
        app=celery_app,
    )

    response = {
        "task_id": task_id,
        "status": task_result.status,
        "result": None,
    }

    if task_result.successful():
        response["result"] = task_result.result

    elif task_result.failed():
        response["result"] = {
            "error": str(task_result.result),
        }

    return response


@router.post(
    "/ingestion/source/async",
    response_model=JobIngestionTaskResponse,
    status_code=202,
)
def enqueue_job_source_ingestion(
    request: JobSourceIngestionRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    task_id = uuid()

    repository = JobIngestionRunRepository(db)

    ingestion_run = repository.create(
        task_id=task_id,
        source=request.source,
    )

    try:
        ingest_job_source_task.apply_async(
            kwargs={
                "run_id": ingestion_run.id,
                "source_name": request.source,
                "query": request.query,
                "location": request.location,
            },
            task_id=task_id,
        )

    except Exception:
        db.rollback()

        repository.mark_failure(
            run=ingestion_run,
            error_message=(
                "Task could not be queued"
            ),
        )

        raise

    return JobIngestionTaskResponse(
        run_id=ingestion_run.id,
        task_id=task_id,
        status=ingestion_run.status,
        source=ingestion_run.source,
    )