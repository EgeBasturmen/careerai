import argparse
import json
import sys

from src.domains.matching.ml.training_dataset_validator import (
    MatchTrainingDatasetValidator,
)

from src.domains.matching.ml.feature_sets import (
    get_feature_set,
)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a CareerAI matching "
            "training dataset."
        )
    )

    parser.add_argument(
        "--dataset",
        default=(
            "datasets/matching/"
            "training_v1.csv"
        ),
        help=(
            "Path to the CSV training dataset."
        ),
    )

    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help=(
            "Return a failing exit code when "
            "validation warnings exist."
        ),
    )

    parser.add_argument(
        "--feature-set",
        default=(
            "match-ranking-ltr:"
            "v2-cross-encoder"
        ),
        help=(
            "Registered feature set identifier "
            "used by the dataset."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    feature_set = get_feature_set(
        args.feature_set,
    )

    validator = (
        MatchTrainingDatasetValidator()
    )

    result = validator.validate_csv(
        dataset_path=args.dataset,
        feature_set=feature_set,
    )

    print(
        json.dumps(
            result.to_dict(),
            indent=2,
            ensure_ascii=False,
        )
    )

    has_warning = any(
        issue.severity == "WARNING"
        for issue in result.issues
    )

    if not result.is_valid:
        sys.exit(1)

    if (
        args.fail_on_warning
        and has_warning
    ):
        sys.exit(2)


if __name__ == "__main__":
    main()