import argparse
import json

from src.domains.matching.ml.lightgbm_ranker_trainer import (
    LightGBMRankerTrainer,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Train a CareerAI LightGBM "
            "Learning-to-Rank model."
        )
    )

    parser.add_argument(
        "--dataset",
        default=(
            "datasets/matching/"
            "training_v2.csv"
        ),
    )

    parser.add_argument(
        "--manifest",
        default=(
            "datasets/matching/"
            "training_v2.csv.manifest.json"
        ),
    )

    parser.add_argument(
        "--model-output",
        default=(
            "artifacts/matching/models/"
            "lightgbm_ranker_v1.joblib"
        ),
    )

    parser.add_argument(
        "--report-output",
        default=(
            "artifacts/matching/reports/"
            "lightgbm_ranker_v1.json"
        ),
    )

    parser.add_argument(
        "--model-version",
        default="v1",
    )

    parser.add_argument(
        "--validation-size",
        type=float,
        default=0.25,
    )

    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    trainer = LightGBMRankerTrainer()

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
        validation_size=(
            args.validation_size
        ),
        random_state=(
            args.random_state
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