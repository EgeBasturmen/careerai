from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class RankedJobPrediction:
    job_id: int
    original_rank: int
    predicted_rank: int
    ranking_score: float
    feature_values: dict[str, float]

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RankingPredictionResult:
    model_name: str
    model_version: str
    feature_set_identifier: str
    pipeline_test_only: bool

    input_count: int
    predictions: list[
        RankedJobPrediction
    ]

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return asdict(self)