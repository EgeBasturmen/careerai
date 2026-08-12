from pydantic import BaseModel


class MLShadowMetricDifference(BaseModel):
    baseline: float | None
    candidate: float | None

    absolute_change: float | None
    percentage_change: float | None

    lower_is_better: bool


class MLShadowEvaluationRunComparisonResponse(
    BaseModel
):
    baseline_run_id: int
    candidate_run_id: int

    same_resume: bool
    same_algorithm_version: bool
    same_feature_set: bool

    baseline_model_name: str | None
    baseline_model_version: str | None

    candidate_model_name: str | None
    candidate_model_version: str | None

    feedback_count_baseline: int
    feedback_count_candidate: int

    successful_prediction_count: (
        MLShadowMetricDifference
    )

    failed_prediction_count: (
        MLShadowMetricDifference
    )

    grade_agreement_rate: (
        MLShadowMetricDifference
    )

    mean_absolute_difference: (
        MLShadowMetricDifference
    )

    hybrid_feedback_mae: (
        MLShadowMetricDifference
    )

    ml_feedback_mae: (
        MLShadowMetricDifference
    )

    recommendation: str