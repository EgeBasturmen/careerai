import argparse
import json

import src.core.database.models  # noqa: F401

from src.core.database.session import (
    SessionLocal,
)
from src.domains.matching.ml.lightgbm_ranker_predictor import (
    LightGBMRankerPredictor,
)
from src.domains.matching.repositories.match_repository import (
    MatchRepository,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Test the CareerAI LightGBM "
            "ranker on persisted matches."
        )
    )

    parser.add_argument(
        "--resume-id",
        type=int,
        required=True,
    )

    parser.add_argument(
        "--model-path",
        default=(
            "artifacts/matching/models/"
            "lightgbm_ranker_v1.joblib"
        ),
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=20,
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.resume_id <= 0:
        raise ValueError(
            "resume-id must be positive"
        )

    if args.limit <= 0:
        raise ValueError(
            "limit must be positive"
        )

    db = SessionLocal()

    try:
        repository = MatchRepository(
            db,
        )

        matches = repository.list_by_resume(
            resume_id=args.resume_id,
        )[: args.limit]

        if not matches:
            raise ValueError(
                "No persisted matches found "
                f"for resume {args.resume_id}"
            )

        predictor = LightGBMRankerPredictor(
            model_path=args.model_path,
        )

        candidates: list[dict] = []

        for match in matches:
            breakdown = (
                match.score_breakdown
                or {}
            )

            matched_skill_count = int(
                breakdown.get(
                    "matched_skill_count",
                    len(
                        match.matched_skills
                        or []
                    ),
                )
                or 0
            )

            missing_skill_count = int(
                breakdown.get(
                    "missing_skill_count",
                    len(
                        match.missing_skills
                        or []
                    ),
                )
                or 0
            )

            required_skill_count = int(
                breakdown.get(
                    "required_skill_count",
                    (
                        matched_skill_count
                        + missing_skill_count
                    ),
                )
                or 0
            )

            skill_match_ratio = (
                matched_skill_count
                / required_skill_count
                if required_skill_count > 0
                else 0.0
            )

            missing_skill_ratio = (
                missing_skill_count
                / required_skill_count
                if required_skill_count > 0
                else 0.0
            )

            skill_coverage_gap = max(
                0.0,
                min(
                    1.0,
                    1.0
                    - skill_match_ratio,
                ),
            )

            feature_values = {
                "skill_score": float(
                    breakdown.get(
                        "skill_score",
                        0.0,
                    )
                    or 0.0
                ),
                "semantic_score": float(
                    breakdown.get(
                        "semantic_score",
                        0.0,
                    )
                    or 0.0
                ),
                "reranker_score": float(
                    breakdown.get(
                        "reranker_score",
                        0.0,
                    )
                    or 0.0
                ),
                "seniority_score": float(
                    breakdown.get(
                        "seniority_score",
                        0.0,
                    )
                    or 0.0
                ),
                "location_score": float(
                    breakdown.get(
                        "location_score",
                        0.0,
                    )
                    or 0.0
                ),
                "matched_skill_count": (
                    matched_skill_count
                ),
                "missing_skill_count": (
                    missing_skill_count
                ),
                "required_skill_count": (
                    required_skill_count
                ),
                "skill_match_ratio": (
                    skill_match_ratio
                ),
                "missing_skill_ratio": (
                    missing_skill_ratio
                ),
                "skill_coverage_gap": (
                    skill_coverage_gap
                ),
            }

            candidates.append(
                {
                    "job_id": match.job_id,
                    "feature_values": (
                        feature_values
                    ),
                }
            )

        result = predictor.rank(
            candidates
        )

        hybrid_scores = {
            match.job_id: float(
                match.match_score
            )
            for match in matches
        }

        output = {
            **result.to_dict(),
            "resume_id": args.resume_id,
            "comparison": [
                {
                    **prediction.to_dict(),
                    "hybrid_score": (
                        hybrid_scores.get(
                            prediction.job_id
                        )
                    ),
                    "rank_change": (
                        prediction.original_rank
                        - prediction.predicted_rank
                    ),
                }
                for prediction
                in result.predictions
            ],
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