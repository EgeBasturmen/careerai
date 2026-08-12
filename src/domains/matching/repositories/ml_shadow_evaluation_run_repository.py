from sqlalchemy.orm import Session

from src.domains.matching.models.ml_shadow_evaluation_run import (
    MLShadowEvaluationRun,
)
from src.domains.matching.schemas.ml_shadow_comparison_schema import (
    MLShadowComparisonResponse,
)


class MLShadowEvaluationRunRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        user_id: int,
        comparison: MLShadowComparisonResponse,
    ) -> MLShadowEvaluationRun:
        run = MLShadowEvaluationRun(
            user_id=user_id,
            resume_id=comparison.resume_id,
            algorithm_version=(
                comparison.algorithm_version
            ),
            ml_model_name=(
                comparison.ml_model_name
            ),
            ml_model_version=(
                comparison.ml_model_version
            ),
            ml_feature_set_identifier=(
                comparison.ml_feature_set_identifier
            ),
            total_match_count=(
                comparison.total_match_count
            ),
            shadow_prediction_count=(
                comparison.shadow_prediction_count
            ),
            feedback_count=(
                comparison.feedback_count
            ),
            successful_prediction_count=(
                comparison.successful_prediction_count
            ),
            failed_prediction_count=(
                comparison.failed_prediction_count
            ),
            model_not_found_count=(
                comparison.model_not_found_count
            ),
            disabled_prediction_count=(
                comparison.disabled_prediction_count
            ),
            mean_absolute_difference=(
                comparison.mean_absolute_difference
            ),
            grade_agreement_rate=(
                comparison.grade_agreement_rate
            ),
            hybrid_feedback_mae=(
                comparison.hybrid_feedback_mae
            ),
            ml_feedback_mae=(
                comparison.ml_feedback_mae
            ),
            recommendation=(
                comparison.recommendation
            ),
            comparisons=[
                item.model_dump()
                for item in comparison.comparisons
            ],
        )

        self.db.add(
            run,
        )

        self.db.commit()
        self.db.refresh(
            run,
        )

        return run

    def get_by_id(
        self,
        run_id: int,
        user_id: int | None = None,
    ) -> MLShadowEvaluationRun | None:
        query = (
            self.db.query(
                MLShadowEvaluationRun
            )
            .filter(
                MLShadowEvaluationRun.id
                == run_id,
            )
        )

        if user_id is not None:
            query = query.filter(
                MLShadowEvaluationRun.user_id
                == user_id,
            )

        return query.first()

    def list_by_resume(
        self,
        user_id: int,
        resume_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MLShadowEvaluationRun]:
        return (
            self.db.query(
                MLShadowEvaluationRun
            )
            .filter(
                MLShadowEvaluationRun.user_id
                == user_id,
                MLShadowEvaluationRun.resume_id
                == resume_id,
            )
            .order_by(
                MLShadowEvaluationRun.id.desc()
            )
            .offset(
                offset
            )
            .limit(
                limit
            )
            .all()
        )