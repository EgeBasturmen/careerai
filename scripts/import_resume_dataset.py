import argparse
import json

import src.core.database.models  # noqa: F401

from src.core.database.session import SessionLocal
from src.domains.resumes.services.resume_dataset_import_service import (
    ResumeDatasetImportService,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Import a directory of resume PDFs "
            "into CareerAI."
        )
    )

    parser.add_argument(
        "--dataset-dir",
        required=True,
        help=(
            "Directory containing resume PDFs. "
            "Subdirectory names are used as categories."
        ),
    )

    parser.add_argument(
        "--dataset-name",
        required=True,
        help="Dataset identifier stored in the database.",
    )

    parser.add_argument(
        "--user-id",
        type=int,
        required=True,
        help=(
            "Existing CareerAI user ID that will own "
            "the imported resume records."
        ),
    )

    parser.add_argument(
        "--source",
        default="kaggle",
        help="Resume source, such as kaggle or internal.",
    )

    parser.add_argument(
        "--output-dir",
        default="uploads/resumes/datasets",
        help=(
            "Directory where imported files "
            "will be copied."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    db = SessionLocal()

    try:
        result = (
            ResumeDatasetImportService(db)
            .import_directory(
                dataset_directory=(
                    args.dataset_dir
                ),
                dataset_name=(
                    args.dataset_name
                ),
                user_id=args.user_id,
                source=args.source,
                output_directory=(
                    args.output_dir
                ),
            )
        )

        print(
            json.dumps(
                result.model_dump(),
                indent=2,
                ensure_ascii=False,
            )
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()