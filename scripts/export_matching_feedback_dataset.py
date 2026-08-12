import argparse
import json

import src.core.database.models  # noqa: F401

from src.core.database.session import (
    SessionLocal,
)
from src.domains.matching.evaluation.feedback_dataset_exporter import (
    MatchFeedbackDatasetExporter,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export matching feedback "
            "as an evaluation dataset."
        )
    )

    parser.add_argument(
        "--output",
        default=(
            "evaluation/matching/"
            "feedback_v1.json"
        ),
    )

    parser.add_argument(
        "--dataset-name",
        default=(
            "careerai-matching-feedback-eval"
        ),
    )

    parser.add_argument(
        "--dataset-version",
        default="feedback-v1",
    )

    parser.add_argument(
        "--minimum-feedback-per-resume",
        type=int,
        default=1,
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.minimum_feedback_per_resume < 1:
        raise ValueError(
            "minimum-feedback-per-resume "
            "must be at least 1"
        )

    db = SessionLocal()

    try:
        exporter = (
            MatchFeedbackDatasetExporter(
                db,
            )
        )

        dataset = exporter.export(
            output_path=args.output,
            dataset_name=args.dataset_name,
            dataset_version=(
                args.dataset_version
            ),
            minimum_feedback_per_resume=(
                args.minimum_feedback_per_resume
            ),
        )

        print(
            json.dumps(
                {
                    "output_path": args.output,
                    "dataset_name": (
                        dataset["dataset_name"]
                    ),
                    "dataset_version": (
                        dataset["dataset_version"]
                    ),
                    "case_count": (
                        dataset["case_count"]
                    ),
                    "feedback_count": (
                        dataset["feedback_count"]
                    ),
                },
                indent=2,
                ensure_ascii=False,
            )
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()