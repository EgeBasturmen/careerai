from datetime import datetime

from pydantic import BaseModel


class MatchingEvaluationRunResponse(BaseModel):
    id: int

    dataset_name: str
    dataset_version: str
    algorithm_version: str

    case_count: int

    mean_precision_at_5: float
    mean_recall_at_5: float
    mean_reciprocal_rank: float
    mean_ndcg_at_5: float

    configuration: dict
    case_results: list[dict]

    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class MatchingMetricDifference(BaseModel):
    baseline: float
    candidate: float
    absolute_change: float
    percentage_change: float | None


class MatchingEvaluationComparisonResponse(BaseModel):
    baseline_run_id: int
    candidate_run_id: int

    same_dataset: bool
    same_dataset_version: bool

    baseline_algorithm_version: str
    candidate_algorithm_version: str

    precision_at_5: MatchingMetricDifference
    recall_at_5: MatchingMetricDifference
    reciprocal_rank: MatchingMetricDifference
    ndcg_at_5: MatchingMetricDifference

    recommendation: str

