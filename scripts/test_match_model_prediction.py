import argparse
import json

from src.domains.matching.ml.match_model_predictor import (
    MatchModelPredictor,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Test the baseline CareerAI "
            "match model prediction pipeline."
        )
    )

    parser.add_argument(
        "--model",
        default=(
            "artifacts/matching/models/"
            "baseline_match_model_v1.joblib"
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    predictor = MatchModelPredictor(
        model_path=args.model,
    )

    feature_values = {
        "skill_score": 25.0,
        "semantic_score": 81.13,
        "seniority_score": 100.0,
        "location_score": 50.0,
        "matched_skill_count": 1,
        "missing_skill_count": 3,
        "required_skill_count": 4,
    }

    result = predictor.predict(
        feature_values=feature_values,
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