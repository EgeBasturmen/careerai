from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class MatchModelPredictionResult:
    model_name: str
    model_version: str
    feature_set_identifier: str

    raw_prediction: float
    predicted_relevance: float
    predicted_grade: int

    feature_values: dict[str, float]

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return asdict(self)