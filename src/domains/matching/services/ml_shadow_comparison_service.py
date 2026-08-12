from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.domains.matching.ml.shadow_prediction_status import (
    ShadowPredictionStatus,
)
from src.domains.matching.repositories.match_feedback_repository import (
    MatchFeedbackRepository,
)
from src.domains.matching.repositories.match_repository import (
    MatchRepository,
)
from src.domains.matching.schemas.ml_shadow_comparison_schema import (
    MLShadowComparisonResponse,
    MLShadowMatchComparison,
)
from src.domains.resumes.repositories.resume_repository import (
    ResumeRepository,
)
from src.domains.users.models.user import User

from src.domains.matching.repositories.ml_shadow_evaluation_run_repository import (
    MLShadowEvaluationRunRepository,
)
from src.domains.matching.schemas.ml_shadow_evaluation_schema import (
    MLShadowEvaluationRunResponse,
)
class MLShadowComparisonService:
    MIN_GRADE = 0
    MAX_GRADE = 3

    def __init__(
        self,
        db: Session,
    ):
        self.resume_repository = ResumeRepository(
            db,
        )

        self.match_repository = MatchRepository(
            db,
        )

        self.feedback_repository = (
            MatchFeedbackRepository(
                db,
            )
        )
        self.evaluation_run_repository = (
            MLShadowEvaluationRunRepository(
                db,
            )
        )

    def compare_for_resume(
        self,
        current_user: User,
        resume_id: int,
    ) -> MLShadowComparisonResponse:
        resume = (
            self.resume_repository
            .get_by_id_and_user(
                resume_id=resume_id,
                user_id=current_user.id,
            )
        )

        if resume is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

        all_matches = (
            self.match_repository
            .list_by_resume(
                resume_id=resume.id,
            )
        )

        shadow_matches = (
            self.match_repository
            .list_shadow_predictions_by_resume(
                resume_id=resume.id,
            )
        )

        status_counts = (
            self.match_repository
            .count_ml_prediction_statuses(
                resume_id=resume.id,
            )
        )

        comparisons: list[
            MLShadowMatchComparison
        ] = []

        absolute_differences: list[float] = []
        grade_agreements: list[bool] = []

        hybrid_feedback_errors: list[float] = []
        ml_feedback_errors: list[float] = []

        for match in shadow_matches:
            if (
                match.ml_predicted_relevance
                is None
            ):
                continue

            hybrid_relevance = (
                self._match_score_to_relevance(
                    match.match_score,
                )
            )

            hybrid_grade = self._to_grade(
                hybrid_relevance,
            )

            ml_relevance = (
                self._clamp_relevance(
                    float(
                        match.ml_predicted_relevance
                    )
                )
            )

            ml_grade = (
                int(
                    match.ml_predicted_grade
                )
                if match.ml_predicted_grade
                is not None
                else self._to_grade(
                    ml_relevance,
                )
            )

            relevance_difference = abs(
                hybrid_relevance
                - ml_relevance
            )

            grades_agree = (
                hybrid_grade == ml_grade
            )

            absolute_differences.append(
                relevance_difference,
            )

            grade_agreements.append(
                grades_agree,
            )

            feedback = (
                self.feedback_repository
                .get_by_user_resume_job(
                    user_id=current_user.id,
                    resume_id=resume.id,
                    job_id=match.job_id,
                )
            )

            feedback_grade: int | None = None
            hybrid_absolute_error: float | None = None
            ml_absolute_error: float | None = None

            if feedback is not None:
                feedback_grade = int(
                    feedback.relevance_grade
                )

                hybrid_absolute_error = abs(
                    hybrid_relevance
                    - feedback_grade
                )

                ml_absolute_error = abs(
                    ml_relevance
                    - feedback_grade
                )

                hybrid_feedback_errors.append(
                    hybrid_absolute_error,
                )

                ml_feedback_errors.append(
                    ml_absolute_error,
                )

            comparisons.append(
                MLShadowMatchComparison(
                    job_id=match.job_id,
                    hybrid_match_score=round(
                        float(
                            match.match_score
                        ),
                        4,
                    ),
                    hybrid_relevance=round(
                        hybrid_relevance,
                        4,
                    ),
                    hybrid_grade=hybrid_grade,
                    ml_predicted_relevance=round(
                        ml_relevance,
                        4,
                    ),
                    ml_predicted_grade=ml_grade,
                    relevance_difference=round(
                        relevance_difference,
                        4,
                    ),
                    grades_agree=grades_agree,
                    feedback_grade=feedback_grade,
                    hybrid_absolute_error=(
                        round(
                            hybrid_absolute_error,
                            4,
                        )
                        if hybrid_absolute_error
                        is not None
                        else None
                    ),
                    ml_absolute_error=(
                        round(
                            ml_absolute_error,
                            4,
                        )
                        if ml_absolute_error
                        is not None
                        else None
                    ),
                )
            )

        first_shadow_match = (
            shadow_matches[0]
            if shadow_matches
            else None
        )

        hybrid_feedback_mae = (
            self._mean_or_none(
                hybrid_feedback_errors,
            )
        )

        ml_feedback_mae = (
            self._mean_or_none(
                ml_feedback_errors,
            )
        )

        return MLShadowComparisonResponse(
            resume_id=resume.id,
            algorithm_version=(
                first_shadow_match.algorithm_version
                if first_shadow_match
                else None
            ),
            ml_model_name=(
                first_shadow_match.ml_model_name
                if first_shadow_match
                else None
            ),
            ml_model_version=(
                first_shadow_match.ml_model_version
                if first_shadow_match
                else None
            ),
            ml_feature_set_identifier=(
                first_shadow_match
                .ml_feature_set_identifier
                if first_shadow_match
                else None
            ),
            total_match_count=len(
                all_matches
            ),
            shadow_prediction_count=len(
                comparisons
            ),
            feedback_count=len(
                hybrid_feedback_errors
            ),
            successful_prediction_count=(
                status_counts.get(
                    ShadowPredictionStatus
                    .SUCCESS
                    .value,
                    0,
                )
            ),
            failed_prediction_count=(
                status_counts.get(
                    ShadowPredictionStatus
                    .FAILURE
                    .value,
                    0,
                )
            ),
            model_not_found_count=(
                status_counts.get(
                    ShadowPredictionStatus
                    .MODEL_NOT_FOUND
                    .value,
                    0,
                )
            ),
            disabled_prediction_count=(
                status_counts.get(
                    ShadowPredictionStatus
                    .DISABLED
                    .value,
                    0,
                )
            ),
            mean_absolute_difference=round(
                self._mean(
                    absolute_differences,
                ),
                4,
            ),
            grade_agreement_rate=round(
                self._agreement_rate(
                    grade_agreements,
                ),
                4,
            ),
            hybrid_feedback_mae=(
                round(
                    hybrid_feedback_mae,
                    4,
                )
                if hybrid_feedback_mae
                is not None
                else None
            ),
            ml_feedback_mae=(
                round(
                    ml_feedback_mae,
                    4,
                )
                if ml_feedback_mae
                is not None
                else None
            ),
            recommendation=(
                self._build_recommendation(
                    feedback_count=len(
                        hybrid_feedback_errors
                    ),
                    hybrid_feedback_mae=(
                        hybrid_feedback_mae
                    ),
                    ml_feedback_mae=(
                        ml_feedback_mae
                    ),
                    successful_prediction_count=(
                        status_counts.get(
                            ShadowPredictionStatus
                            .SUCCESS
                            .value,
                            0,
                        )
                    ),
                    failed_prediction_count=(
                        status_counts.get(
                            ShadowPredictionStatus
                            .FAILURE
                            .value,
                            0,
                        )
                    ),
                )
            ),
            comparisons=comparisons,
        )

    def _match_score_to_relevance(
        self,
        match_score: float,
    ) -> float:
        normalized_score = max(
            0.0,
            min(
                float(match_score),
                100.0,
            ),
        )

        return (
            normalized_score / 100.0
        ) * self.MAX_GRADE

    def _to_grade(
        self,
        relevance: float,
    ) -> int:
        grade = round(
            self._clamp_relevance(
                relevance,
            )
        )

        return max(
            self.MIN_GRADE,
            min(
                int(grade),
                self.MAX_GRADE,
            ),
        )

    def _clamp_relevance(
        self,
        relevance: float,
    ) -> float:
        return max(
            float(
                self.MIN_GRADE
            ),
            min(
                float(relevance),
                float(
                    self.MAX_GRADE
                ),
            ),
        )

    def _mean(
        self,
        values: list[float],
    ) -> float:
        if not values:
            return 0.0

        return sum(values) / len(
            values
        )

    def _mean_or_none(
        self,
        values: list[float],
    ) -> float | None:
        if not values:
            return None

        return self._mean(
            values,
        )

    def _agreement_rate(
        self,
        agreements: list[bool],
    ) -> float:
        if not agreements:
            return 0.0

        agreement_count = sum(
            1
            for agreement in agreements
            if agreement
        )

        return (
            agreement_count
            / len(agreements)
        )

    def _build_recommendation(
        self,
        feedback_count: int,
        hybrid_feedback_mae: float | None,
        ml_feedback_mae: float | None,
        successful_prediction_count: int,
        failed_prediction_count: int,
    ) -> str:
        if successful_prediction_count == 0:
            return (
                "No successful ML shadow predictions "
                "are available. Check the model artifact "
                "and shadow inference configuration."
            )

        if failed_prediction_count > 0:
            return (
                "Some ML shadow predictions failed. "
                "Review prediction errors before "
                "evaluating the model."
            )

        if feedback_count == 0:
            return (
                "No user feedback is available. "
                "The ML model must remain in shadow mode."
            )

        if feedback_count < 20:
            return (
                "There are too few labeled examples "
                "to make a reliable production decision. "
                "Keep the ML model in shadow mode."
            )

        if (
            hybrid_feedback_mae is None
            or ml_feedback_mae is None
        ):
            return (
                "Feedback metrics could not be "
                "calculated. Keep the ML model in "
                "shadow mode."
            )

        if ml_feedback_mae < hybrid_feedback_mae:
            return (
                "The ML shadow model is closer to "
                "user feedback than the hybrid engine, "
                "but further evaluation is required "
                "before promotion."
            )

        if ml_feedback_mae > hybrid_feedback_mae:
            return (
                "The ML shadow model performs worse "
                "than the hybrid engine on available "
                "feedback. Do not promote it."
            )

        return (
            "The ML shadow model and hybrid engine "
            "have similar feedback error. Continue "
            "collecting labeled data."
        )
    
    def compare_and_save_for_resume(
        self,
        current_user: User,
        resume_id: int,
    ) -> MLShadowEvaluationRunResponse:
        comparison = self.compare_for_resume(
            current_user=current_user,
            resume_id=resume_id,
        )

        saved_run = (
            self.evaluation_run_repository.create(
                user_id=current_user.id,
                comparison=comparison,
            )
        )

        return (
            MLShadowEvaluationRunResponse
            .model_validate(
                saved_run
            )
        )