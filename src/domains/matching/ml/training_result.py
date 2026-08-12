from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class MatchModelTrainingResult:
    model_name: str
    model_version: str

    dataset_path: str
    manifest_path: str
    feature_set_identifier: str

    row_count: int
    train_row_count: int
    test_row_count: int

    mean_absolute_error: float | None
    root_mean_squared_error: float | None
    r2_score: float | None

    model_path: str
    report_path: str

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return asdict(self)