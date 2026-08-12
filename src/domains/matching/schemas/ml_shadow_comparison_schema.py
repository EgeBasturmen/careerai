from pydantic import BaseModel


class MLShadowMatchComparison(BaseModel):
    job_id: int

    hybrid_match_score: float
    hybrid_relevance: float
    hybrid_grade: int

    ml_predicted_relevance: float
    ml_predicted_grade: int

    relevance_difference: float
    grades_agree: bool

    feedback_grade: int | None

    hybrid_absolute_error: float | None
    ml_absolute_error: float | None


class MLShadowComparisonResponse(BaseModel):
    resume_id: int

    algorithm_version: str | None
    ml_model_name: str | None
    ml_model_version: str | None
    ml_feature_set_identifier: str | None

    total_match_count: int
    shadow_prediction_count: int
    feedback_count: int

    mean_absolute_difference: float
    grade_agreement_rate: float

    hybrid_feedback_mae: float | None
    ml_feedback_mae: float | None

    recommendation: str
    successful_prediction_count: int
    failed_prediction_count: int
    model_not_found_count: int
    disabled_prediction_count: int

    comparisons: list[
        MLShadowMatchComparison
    ]