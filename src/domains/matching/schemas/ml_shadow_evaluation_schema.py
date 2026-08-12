from datetime import datetime

from pydantic import BaseModel


class MLShadowEvaluationRunResponse(BaseModel):
    id: int

    user_id: int
    resume_id: int

    algorithm_version: str | None
    ml_model_name: str | None
    ml_model_version: str | None
    ml_feature_set_identifier: str | None

    total_match_count: int
    shadow_prediction_count: int
    feedback_count: int

    successful_prediction_count: int
    failed_prediction_count: int
    model_not_found_count: int
    disabled_prediction_count: int

    mean_absolute_difference: float
    grade_agreement_rate: float

    hybrid_feedback_mae: float | None
    ml_feedback_mae: float | None

    recommendation: str

    comparisons: list[dict]

    created_at: datetime

    model_config = {
        "from_attributes": True,
    }