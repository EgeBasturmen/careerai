from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.domains.matching.repositories.ml_shadow_evaluation_run_repository import (
    MLShadowEvaluationRunRepository,
)
from src.domains.matching.schemas.ml_shadow_evaluation_comparison_schema import (
    MLShadowEvaluationRunComparisonResponse,
    MLShadowMetricDifference,
)
from src.domains.users.models.user import User


class MLShadowEvaluationComparisonService:
    def __init__(
        self,
        db: Session,
    ):
        self.repository = (
            MLShadowEvaluationRunRepository(
                db,
            )
        )

    def compare(
        self,
        current_user: User,
        baseline_run_id: int,
        candidate_run_id: int,
    ) -> MLShadowEvaluationRunComparisonResponse:
        if baseline_run_id == candidate_run_id:
            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Baseline and candidate run IDs "
                    "must be different"
                ),
            )

        baseline_run = (
            self.repository.get_by_id(
                run_id=baseline_run_id,
                user_id=current_user.id,
            )
        )

        if baseline_run is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_404_NOT_FOUND
                ),
                detail=(
                    "Baseline ML shadow evaluation "
                    "run not found"
                ),
            )

        candidate_run = (
            self.repository.get_by_id(
                run_id=candidate_run_id,
                user_id=current_user.id,
            )
        )

        if candidate_run is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_404_NOT_FOUND
                ),
                detail=(
                    "Candidate ML shadow evaluation "
                    "run not found"
                ),
            )

        same_resume = (
            baseline_run.resume_id
            == candidate_run.resume_id
        )

        same_algorithm_version = (
            baseline_run.algorithm_version
            == candidate_run.algorithm_version
        )

        same_feature_set = (
            baseline_run.ml_feature_set_identifier
            == candidate_run.ml_feature_set_identifier
        )

        success_difference = (
            self._build_difference(
                baseline=float(
                    baseline_run
                    .successful_prediction_count
                ),
                candidate=float(
                    candidate_run
                    .successful_prediction_count
                ),
                lower_is_better=False,
            )
        )

        failure_difference = (
            self._build_difference(
                baseline=float(
                    baseline_run
                    .failed_prediction_count
                ),
                candidate=float(
                    candidate_run
                    .failed_prediction_count
                ),
                lower_is_better=True,
            )
        )

        agreement_difference = (
            self._build_difference(
                baseline=(
                    baseline_run
                    .grade_agreement_rate
                ),
                candidate=(
                    candidate_run
                    .grade_agreement_rate
                ),
                lower_is_better=False,
            )
        )

        absolute_difference_change = (
            self._build_difference(
                baseline=(
                    baseline_run
                    .mean_absolute_difference
                ),
                candidate=(
                    candidate_run
                    .mean_absolute_difference
                ),
                lower_is_better=True,
            )
        )

        hybrid_mae_difference = (
            self._build_difference(
                baseline=(
                    baseline_run
                    .hybrid_feedback_mae
                ),
                candidate=(
                    candidate_run
                    .hybrid_feedback_mae
                ),
                lower_is_better=True,
            )
        )

        ml_mae_difference = (
            self._build_difference(
                baseline=(
                    baseline_run
                    .ml_feedback_mae
                ),
                candidate=(
                    candidate_run
                    .ml_feedback_mae
                ),
                lower_is_better=True,
            )
        )

        recommendation = (
            self._build_recommendation(
                same_resume=same_resume,
                same_algorithm_version=(
                    same_algorithm_version
                ),
                baseline_feedback_count=(
                    baseline_run.feedback_count
                ),
                candidate_feedback_count=(
                    candidate_run.feedback_count
                ),
                baseline_failure_count=(
                    baseline_run
                    .failed_prediction_count
                ),
                candidate_failure_count=(
                    candidate_run
                    .failed_prediction_count
                ),
                baseline_ml_mae=(
                    baseline_run.ml_feedback_mae
                ),
                candidate_ml_mae=(
                    candidate_run.ml_feedback_mae
                ),
                baseline_grade_agreement=(
                    baseline_run
                    .grade_agreement_rate
                ),
                candidate_grade_agreement=(
                    candidate_run
                    .grade_agreement_rate
                ),
            )
        )

        return (
            MLShadowEvaluationRunComparisonResponse(
                baseline_run_id=(
                    baseline_run.id
                ),
                candidate_run_id=(
                    candidate_run.id
                ),
                same_resume=same_resume,
                same_algorithm_version=(
                    same_algorithm_version
                ),
                same_feature_set=(
                    same_feature_set
                ),
                baseline_model_name=(
                    baseline_run.ml_model_name
                ),
                baseline_model_version=(
                    baseline_run.ml_model_version
                ),
                candidate_model_name=(
                    candidate_run.ml_model_name
                ),
                candidate_model_version=(
                    candidate_run.ml_model_version
                ),
                feedback_count_baseline=(
                    baseline_run.feedback_count
                ),
                feedback_count_candidate=(
                    candidate_run.feedback_count
                ),
                successful_prediction_count=(
                    success_difference
                ),
                failed_prediction_count=(
                    failure_difference
                ),
                grade_agreement_rate=(
                    agreement_difference
                ),
                mean_absolute_difference=(
                    absolute_difference_change
                ),
                hybrid_feedback_mae=(
                    hybrid_mae_difference
                ),
                ml_feedback_mae=(
                    ml_mae_difference
                ),
                recommendation=(
                    recommendation
                ),
            )
        )

    def _build_difference(
        self,
        baseline: float | None,
        candidate: float | None,
        lower_is_better: bool,
    ) -> MLShadowMetricDifference:
        if (
            baseline is None
            or candidate is None
        ):
            return MLShadowMetricDifference(
                baseline=baseline,
                candidate=candidate,
                absolute_change=None,
                percentage_change=None,
                lower_is_better=(
                    lower_is_better
                ),
            )

        absolute_change = (
            candidate - baseline
        )

        percentage_change: float | None = None

        if baseline != 0:
            percentage_change = (
                absolute_change
                / abs(baseline)
            ) * 100

        return MLShadowMetricDifference(
            baseline=round(
                baseline,
                6,
            ),
            candidate=round(
                candidate,
                6,
            ),
            absolute_change=round(
                absolute_change,
                6,
            ),
            percentage_change=(
                round(
                    percentage_change,
                    2,
                )
                if percentage_change
                is not None
                else None
            ),
            lower_is_better=(
                lower_is_better
            ),
        )

    def _build_recommendation(
        self,
        same_resume: bool,
        same_algorithm_version: bool,
        baseline_feedback_count: int,
        candidate_feedback_count: int,
        baseline_failure_count: int,
        candidate_failure_count: int,
        baseline_ml_mae: float | None,
        candidate_ml_mae: float | None,
        baseline_grade_agreement: float,
        candidate_grade_agreement: float,
    ) -> str:
        if not same_resume:
            return (
                "The runs belong to different "
                "resumes. Do not treat this as a "
                "direct model comparison."
            )

        if not same_algorithm_version:
            return (
                "The hybrid algorithm versions are "
                "different. The result includes both "
                "ML model and hybrid engine changes."
            )

        if (
            baseline_feedback_count
            != candidate_feedback_count
        ):
            return (
                "The runs contain different feedback "
                "counts. Compare the results with "
                "caution."
            )

        if candidate_failure_count > 0:
            return (
                "The candidate model has failed "
                "predictions. Do not promote it."
            )

        if (
            candidate_failure_count
            > baseline_failure_count
        ):
            return (
                "The candidate model has more "
                "prediction failures than the "
                "baseline."
            )

        if (
            baseline_feedback_count < 20
            or candidate_feedback_count < 20
        ):
            return (
                "There are too few labeled examples "
                "for a reliable promotion decision. "
                "Keep both models in shadow mode."
            )

        if (
            baseline_ml_mae is None
            or candidate_ml_mae is None
        ):
            return (
                "ML feedback MAE could not be "
                "calculated for both runs."
            )

        mae_improved = (
            candidate_ml_mae
            < baseline_ml_mae
        )

        agreement_improved = (
            candidate_grade_agreement
            > baseline_grade_agreement
        )

        if (
            mae_improved
            and agreement_improved
        ):
            return (
                "The candidate model improved both "
                "feedback MAE and grade agreement. "
                "Continue shadow evaluation before "
                "promotion."
            )

        if (
            candidate_ml_mae
            > baseline_ml_mae
        ):
            return (
                "The candidate model has worse "
                "feedback MAE than the baseline. "
                "Do not promote it."
            )

        if (
            candidate_grade_agreement
            < baseline_grade_agreement
        ):
            return (
                "The candidate model has lower grade "
                "agreement than the baseline."
            )

        return (
            "The candidate and baseline models have "
            "similar shadow performance."
        )