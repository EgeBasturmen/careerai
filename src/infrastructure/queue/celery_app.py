from celery import Celery

from src.core.config.settings import settings
from src.infrastructure.scheduler.schedules import (
    CELERY_BEAT_SCHEDULE,
)

redis_url = (
    f"redis://{settings.redis_host}:"
    f"{settings.redis_port}/0"
)


celery_app = Celery(
    "careerai",
    broker=redis_url,
    backend=redis_url,
    include=[
        "src.infrastructure.queue.resume_tasks",
        "src.infrastructure.queue.job_ingestion_tasks",
        "src.infrastructure.queue.job_source_tasks",
        "src.infrastructure.queue.rag_evaluation_tasks",
        "src.infrastructure.queue.job_lifecycle_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Istanbul",
    enable_utc=True,
    task_track_started=True,
    beat_schedule=CELERY_BEAT_SCHEDULE,
)