import argparse
import json
from pathlib import Path

import src.core.database.models  # noqa: F401

from src.core.database.session import (
    SessionLocal,
)
from src.domains.jobs.repositories.job_repository import (
    JobRepository,
)
from src.domains.matching.repositories.match_feedback_repository import (
    MatchFeedbackRepository,
)
from src.domains.matching.repositories.match_repository import (
    MatchRepository,
)
from src.domains.resumes.repositories.resume_repository import (
    ResumeRepository,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Import relevance labels for "
            "CareerAI resume-job matches."
        )
    )

    parser.add_argument(
        "--input",
        required=True,
        help=(
            "Path to the JSON label file."
        ),
    )

    parser.add_argument(
        "--user-id",
        type=int,
        required=True,
        help=(
            "User ID that owns the resume "
            "and feedback records."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_path = Path(
        args.input,
    )

    if not input_path.exists():
        raise FileNotFoundError(
            f"Label file not found: {input_path}"
        )

    raw_data = json.loads(
        input_path.read_text(
            encoding="utf-8",
        )
    )

    resume_id = int(
        raw_data["resume_id"]
    )

    labels = raw_data.get(
        "labels",
        [],
    )

    db = SessionLocal()

    try:
        resume_repository = (
            ResumeRepository(db)
        )
        job_repository = (
            JobRepository(db)
        )
        match_repository = (
            MatchRepository(db)
        )
        feedback_repository = (
            MatchFeedbackRepository(db)
        )

        resume = (
            resume_repository
            .get_by_id_and_user(
                resume_id=resume_id,
                user_id=args.user_id,
            )
        )

        if resume is None:
            raise ValueError(
                "Resume not found or does not "
                "belong to the supplied user"
            )

        imported_count = 0
        updated_count = 0
        skipped_count = 0
        failed_count = 0

        results: list[dict] = []
        errors: list[str] = []

        for item in labels:
            try:
                job_id = int(
                    item["job_id"]
                )

                relevance_grade = int(
                    item["relevance_grade"]
                )

                notes = item.get(
                    "notes",
                )

                if relevance_grade not in {
                    0,
                    1,
                    2,
                    3,
                }:
                    raise ValueError(
                        "relevance_grade must be "
                        "one of 0, 1, 2 or 3"
                    )

                job = (
                    job_repository.get_by_id(
                        job_id,
                    )
                )

                if job is None:
                    skipped_count += 1

                    results.append(
                        {
                            "job_id": job_id,
                            "status": "skipped",
                            "reason": "Job not found",
                        }
                    )
                    continue

                match = (
                    match_repository
                    .get_by_resume_and_job(
                        resume_id=resume_id,
                        job_id=job_id,
                    )
                )

                if match is None:
                    skipped_count += 1

                    results.append(
                        {
                            "job_id": job_id,
                            "status": "skipped",
                            "reason": (
                                "Match record not found"
                            ),
                        }
                    )
                    continue

                existing_feedback = (
                    feedback_repository
                    .get_by_user_resume_job(
                        user_id=args.user_id,
                        resume_id=resume_id,
                        job_id=job_id,
                    )
                )

                feedback_repository.upsert(
                    user_id=args.user_id,
                    resume_id=resume_id,
                    job_id=job_id,
                    relevance_grade=(
                        relevance_grade
                    ),
                    notes=notes,
                )

                if existing_feedback is None:
                    imported_count += 1
                    status = "imported"
                else:
                    updated_count += 1
                    status = "updated"

                results.append(
                    {
                        "job_id": job_id,
                        "status": status,
                        "relevance_grade": (
                            relevance_grade
                        ),
                    }
                )

            except Exception as exc:
                db.rollback()

                failed_count += 1

                error_message = (
                    f"{type(exc).__name__}: {exc}"
                )

                errors.append(
                    error_message
                )

                results.append(
                    {
                        "job_id": item.get(
                            "job_id",
                        ),
                        "status": "failed",
                        "error": error_message,
                    }
                )

        output = {
            "input_path": str(
                input_path
            ),
            "user_id": args.user_id,
            "resume_id": resume_id,
            "label_count": len(labels),
            "imported_count": imported_count,
            "updated_count": updated_count,
            "skipped_count": skipped_count,
            "failed_count": failed_count,
            "results": results,
            "errors": errors,
        }

        print(
            json.dumps(
                output,
                indent=2,
                ensure_ascii=False,
            )
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()