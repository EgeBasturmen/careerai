from celery.schedules import crontab


CELERY_BEAT_SCHEDULE = {
    "deactivate-stale-jobs-daily": {
        "task": "jobs.deactivate_stale_jobs",
        "schedule": crontab(
            hour=3,
            minute=0,
        ),
        "kwargs": {
            "stale_days": 30,
        },
    },
}