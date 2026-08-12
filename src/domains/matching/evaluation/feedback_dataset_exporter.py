import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from src.domains.matching.repositories.match_feedback_repository import (
    MatchFeedbackRepository,
)


class MatchFeedbackDatasetExporter:
    def __init__(
        self,
        db: Session,
    ):
        self.feedback_repository = (
            MatchFeedbackRepository(
                db,
            )
        )

    def export(
        self,
        output_path: str,
        dataset_name: str,
        dataset_version: str,
        minimum_feedback_per_resume: int = 1,
    ) -> dict:
        feedback_records = (
            self.feedback_repository.list_all(
                minimum_feedback_per_resume=(
                    minimum_feedback_per_resume
                ),
            )
        )

        grouped_feedback: dict[
            tuple[int, int],
            dict[int, int],
        ] = defaultdict(dict)

        for feedback in feedback_records:
            key = (
                feedback.user_id,
                feedback.resume_id,
            )

            grouped_feedback[key][
                feedback.job_id
            ] = feedback.relevance_grade

        cases: list[dict] = []

        for (
            user_id,
            resume_id,
        ), relevance_grades in grouped_feedback.items():
            cases.append(
                {
                    "name": (
                        f"user-{user_id}-"
                        f"resume-{resume_id}"
                    ),
                    "user_id": user_id,
                    "resume_id": resume_id,
                    "relevance_grades": {
                        str(job_id): grade
                        for job_id, grade
                        in sorted(
                            relevance_grades.items()
                        )
                    },
                }
            )

        dataset = {
            "dataset_name": dataset_name,
            "dataset_version": dataset_version,
            "generated_at": datetime.now(
                timezone.utc,
            ).isoformat(),
            "source": "match_feedback",
            "case_count": len(cases),
            "feedback_count": len(
                feedback_records
            ),
            "cases": cases,
        }

        path = Path(output_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            json.dumps(
                dataset,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return dataset