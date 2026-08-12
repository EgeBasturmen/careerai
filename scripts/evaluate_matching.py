import argparse
import json
from dataclasses import asdict

import src.core.database.models  # noqa: F401

from src.core.database.session import (
    SessionLocal,
)
from src.domains.matching.evaluation.dataset_loader import (
    MatchingEvaluationDatasetLoader,
)
from src.domains.matching.evaluation.evaluator import (
    MatchingEvaluator,
)
from src.domains.matching.repositories.matching_evaluation_run_repository import (
    MatchingEvaluationRunRepository,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate the CareerAI matching "
            "algorithm using a JSON dataset."
        )
    )

    parser.add_argument(
        "--dataset",
        default=(
            "evaluation/matching/"
            "hybrid_v1.json"
        ),
        help=(
            "Path to the matching evaluation "
            "dataset JSON file."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    db = SessionLocal()

    try:
        dataset = (
            MatchingEvaluationDatasetLoader()
            .load(
                args.dataset,
            )
        )

        evaluator = MatchingEvaluator(
            db,
        )

        result = evaluator.evaluate(
            dataset,
        )

        repository = (
            MatchingEvaluationRunRepository(
                db,
            )
        )

        saved_run = repository.create(
            dataset_name=(
                result.dataset_name
            ),
            dataset_version=(
                result.dataset_version
            ),
            algorithm_version=(
                result.algorithm_version
            ),
            case_count=(
                result.case_count
            ),
            mean_precision_at_5=(
                result.mean_precision_at_5
            ),
            mean_recall_at_5=(
                result.mean_recall_at_5
            ),
            mean_reciprocal_rank=(
                result.mean_reciprocal_rank
            ),
            mean_ndcg_at_5=(
                result.mean_ndcg_at_5
            ),
            configuration=(
                result.configuration
            ),
            case_results=[
                asdict(case_result)
                for case_result in result.cases
            ],
        )

        output = {
            "saved_run_id": saved_run.id,
            "dataset_path": args.dataset,
            "evaluation": asdict(
                result,
            ),
        }

        print(
            json.dumps(
                output,
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