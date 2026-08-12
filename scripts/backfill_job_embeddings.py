import src.core.database.models  # noqa: F401

from src.core.database.session import SessionLocal
from src.domains.embeddings.services.job_embedding_service import (
    JobEmbeddingService,
)
from src.domains.jobs.models.job import Job


def main() -> None:
    db = SessionLocal()

    try:
        jobs = db.query(Job).all()

        service = JobEmbeddingService(
            db,
        )

        for job in jobs:
            service.generate_and_save(
                job,
            )

            print(
                f"Embedded job {job.id}: {job.title}"
            )

        print(
            f"Backfilled {len(jobs)} job embeddings."
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()