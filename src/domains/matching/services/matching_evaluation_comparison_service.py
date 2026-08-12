from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.domains.matching.repositories.matching_evaluation_run_repository import (
    MatchingEvaluationRunRepository,
)
from src.domains.matching.schemas.matching_evaluation_schema import (
    MatchingEvaluationComparisonResponse,
    MatchingMetricDifference,
)


class MatchingEvaluationComparisonService:
    def __init__(
        self,
        db: Session,
    ):
        self.repository = (
            MatchingEvaluationRunRepository(
                db,
            )
        )

    def compare(
        self,
        baseline_run_id: int,
        candidate_run_id: int,
    ) -> MatchingEvaluationComparisonResponse:
        baseline_run = self.repository.get_by_id(
            baseline_run_id,
        )

        if baseline_run is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Baseline evaluation run not found"
                ),
            )

        candidate_run = self.repository.get_by_id(
            candidate_run_id,
        )

        if candidate_run is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Candidate evaluation run not found"
                ),
            )

        same_dataset = (
            baseline_run.dataset_name
            == candidate_run.dataset_name
        )

        same_dataset_version = (
            baseline_run.dataset_version
            == candidate_run.dataset_version
        )

        precision_difference = self._build_difference(
            baseline_run.mean_precision_at_5,
            candidate_run.mean_precision_at_5,
        )

        recall_difference = self._build_difference(
            baseline_run.mean_recall_at_5,
            candidate_run.mean_recall_at_5,
        )

        reciprocal_rank_difference = (
            self._build_difference(
                baseline_run.mean_reciprocal_rank,
                candidate_run.mean_reciprocal_rank,
            )
        )

        ndcg_difference = self._build_difference(
            baseline_run.mean_ndcg_at_5,
            candidate_run.mean_ndcg_at_5,
        )

        recommendation = (
            self._build_recommendation(
                same_dataset=same_dataset,
                same_dataset_version=(
                    same_dataset_version
                ),
                ndcg_change=(
                    ndcg_difference.absolute_change
                ),
                mrr_change=(
                    reciprocal_rank_difference
                    .absolute_change
                ),
            )
        )

        return MatchingEvaluationComparisonResponse(
            baseline_run_id=baseline_run.id,
            candidate_run_id=candidate_run.id,
            same_dataset=same_dataset,
            same_dataset_version=(
                same_dataset_version
            ),
            baseline_algorithm_version=(
                baseline_run.algorithm_version
            ),
            candidate_algorithm_version=(
                candidate_run.algorithm_version
            ),
            precision_at_5=precision_difference,
            recall_at_5=recall_difference,
            reciprocal_rank=(
                reciprocal_rank_difference
            ),
            ndcg_at_5=ndcg_difference,
            recommendation=recommendation,
        )

    def _build_difference(
        self,
        baseline: float,
        candidate: float,
    ) -> MatchingMetricDifference:
        absolute_change = candidate - baseline

        percentage_change: float | None = None

        if baseline != 0:
            percentage_change = (
                absolute_change
                / abs(baseline)
            ) * 100

        return MatchingMetricDifference(
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
                if percentage_change is not None
                else None
            ),
        )

    def _build_recommendation(
        self,
        same_dataset: bool,
        same_dataset_version: bool,
        ndcg_change: float,
        mrr_change: float,
    ) -> str:
        if (
            not same_dataset
            or not same_dataset_version
        ):
            return (
                "The runs use different datasets or "
                "dataset versions. Do not treat the "
                "metric difference as a direct "
                "algorithm comparison."
            )

        if (
            ndcg_change > 0
            and mrr_change >= 0
        ):
            return (
                "The candidate ranking appears better "
                "than the baseline on this dataset."
            )

        if (
            ndcg_change < 0
            or mrr_change < 0
        ):
            return (
                "The candidate ranking regressed on "
                "at least one primary ranking metric."
            )

        return (
            "The candidate and baseline have similar "
            "ranking performance on this dataset."
        )