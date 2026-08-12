from src.core.database.session import SessionLocal
from src.domains.jobs.models.job import Job
from src.domains.jobs.services.job_fingerprint_service import (
    JobFingerprintService,
)
from src.domains.jobs.services.job_normalizer import (
    JobNormalizer,
)


def main() -> None:
    db = SessionLocal()

    normalizer = JobNormalizer()
    fingerprint_service = JobFingerprintService()

    try:
        jobs = db.query(Job).all()

        for job in jobs:
            job.normalized_title = (
                normalizer.normalize_title(
                    job.title,
                )
            )

            job.normalized_company_name = (
                normalizer.normalize_company_name(
                    job.company_name,
                )
            )

            job.normalized_location = (
                normalizer.normalize_location(
                    job.location,
                )
            )

            job.fingerprint = (
                fingerprint_service.generate(
                    title=job.title,
                    company_name=job.company_name,
                    location=job.location,
                    description=job.description,
                )
            )

        db.commit()

        print(
            f"Backfilled {len(jobs)} jobs."
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()