import argparse
import json

from src.domains.matching.ml.baseline_match_model_trainer import (
    BaselineMatchModelTrainer,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Train a baseline CareerAI "
            "matching model."
        )
    )

    parser.add_argument(
        "--dataset",
        default=(
            "datasets/matching/"
            "training_v1.csv"
        ),
    )

    parser.add_argument(
        "--manifest",
        default=(
            "datasets/matching/"
            "training_v1.csv.manifest.json"
        ),
    )

    parser.add_argument(
        "--model-output",
        default=(
            "artifacts/matching/models/"
            "baseline_match_model_v1.joblib"
        ),
    )

    parser.add_argument(
        "--report-output",
        default=(
            "artifacts/matching/reports/"
            "baseline_match_model_v1.json"
        ),
    )

    parser.add_argument(
        "--model-version",
        default="v1",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    trainer = (
        BaselineMatchModelTrainer()
    )

    result = trainer.train(
        dataset_path=args.dataset,
        manifest_path=args.manifest,
        model_output_path=(
            args.model_output
        ),
        report_output_path=(
            args.report_output
        ),
        model_version=(
            args.model_version
        ),
    )

    print(
        json.dumps(
            result.to_dict(),
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()