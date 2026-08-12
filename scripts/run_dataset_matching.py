import argparse
import json
from types import SimpleNamespace

import src.core.database.models  # noqa: F401

from src.core.database.session import (
    SessionLocal,
)
from src.domains.matching.services.matching_service import (
    MatchingService,
)
from src.domains.resumes.repositories.resume_repository import (
    ResumeRepository,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run CareerAI matching for every "
            "resume in a dataset."
        )
    )

    parser.add_argument(
        "--dataset-name",
        required=True,
        help=(
            "Dataset name stored in the "
            "resumes table."
        ),
    )

    parser.add_argument(
        "--dataset-category",
        default=None,
        help=(
            "Optionally process only one "
            "dataset category."
        ),
    )

    parser.add_argument(
        "--limit-per-resume",
        type=int,
        default=20,
        help=(
            "Maximum number of matches "
            "returned and persisted per resume."
        ),
    )

    parser.add_argument(
        "--candidate-limit",
        type=int,
        default=100,
        help=(
            "Number of semantic candidates "
            "considered per resume."
        ),
    )

    parser.add_argument(
        "--minimum-similarity",
        type=float,
        default=0.0,
        help=(
            "Minimum semantic similarity "
            "for candidate generation."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.limit_per_resume < 1:
        raise ValueError(
            "limit-per-resume must be positive"
        )

    if args.candidate_limit < 1:
        raise ValueError(
            "candidate-limit must be positive"
        )

    db = SessionLocal()

    try:
        resume_repository = (
            ResumeRepository(db)
        )

        resumes = (
            resume_repository.list_by_dataset(
                dataset_name=args.dataset_name,
                dataset_category=(
                    args.dataset_category
                ),
                limit=10000,
                offset=0,
            )
        )

        matching_service = (
            MatchingService(db)
        )

        processed_count = 0
        skipped_count = 0
        failed_count = 0
        total_match_count = 0

        results: list[dict] = []
        errors: list[str] = []

        for resume in resumes:
            if (
                resume.status != "COMPLETED"
                or resume.parsed_profile is None
            ):
                skipped_count += 1

                results.append(
                    {
                        "resume_id": resume.id,
                        "status": "skipped",
                        "reason": (
                            "Resume is not completed "
                            "or has no parsed profile"
                        ),
                    }
                )
                continue

            try:
                current_user = SimpleNamespace(
                    id=resume.user_id,
                )

                response = (
                    matching_service
                    .match_resume_to_jobs(
                        current_user=current_user,
                        resume_id=resume.id,
                        limit=(
                            args.limit_per_resume
                        ),
                        offset=0,
                        candidate_limit=(
                            args.candidate_limit
                        ),
                        minimum_similarity=(
                            args.minimum_similarity
                        ),
                    )
                )

                processed_count += 1
                total_match_count += (
                    response.returned_count
                )

                results.append(
                    {
                        "resume_id": resume.id,
                        "status": "completed",
                        "returned_count": (
                            response.returned_count
                        ),
                        "job_ids": [
                            match.job_id
                            for match
                            in response.matches
                        ],
                    }
                )

            except Exception as exc:
                db.rollback()

                failed_count += 1

                error_message = (
                    f"Resume {resume.id}: "
                    f"{type(exc).__name__}: "
                    f"{exc}"
                )

                errors.append(
                    error_message
                )

                results.append(
                    {
                        "resume_id": resume.id,
                        "status": "failed",
                        "error": error_message,
                    }
                )

        output = {
            "dataset_name": (
                args.dataset_name
            ),
            "dataset_category": (
                args.dataset_category
            ),
            "discovered_resume_count": len(
                resumes
            ),
            "processed_count": processed_count,
            "skipped_count": skipped_count,
            "failed_count": failed_count,
            "total_match_count": (
                total_match_count
            ),
            "algorithm_versions": sorted(
                {
                    match.get(
                        "algorithm_version"
                    )
                    for match in []
                }
            ),
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