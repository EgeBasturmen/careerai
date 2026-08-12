from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class RankingModelTrainingResult:
    model_name: str
    model_version: str

    dataset_path: str
    manifest_path: str
    feature_set_identifier: str

    row_count: int
    group_count: int

    train_row_count: int
    validation_row_count: int

    train_group_count: int
    validation_group_count: int

    ndcg_at_5: float | None
    mean_reciprocal_rank: float | None

    model_path: str
    report_path: str

    pipeline_test_only: bool

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return asdict(self)