from sqlalchemy.orm import Session

from src.domains.matching.models.matching_evaluation_run import (
    MatchingEvaluationRun,
)


class MatchingEvaluationRunRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        dataset_name: str,
        dataset_version: str,
        algorithm_version: str,
        case_count: int,
        mean_precision_at_5: float,
        mean_recall_at_5: float,
        mean_reciprocal_rank: float,
        mean_ndcg_at_5: float,
        configuration: dict,
        case_results: list[dict],
    ) -> MatchingEvaluationRun:
        evaluation_run = MatchingEvaluationRun(
            dataset_name=dataset_name,
            dataset_version=dataset_version,
            algorithm_version=algorithm_version,
            case_count=case_count,
            mean_precision_at_5=mean_precision_at_5,
            mean_recall_at_5=mean_recall_at_5,
            mean_reciprocal_rank=mean_reciprocal_rank,
            mean_ndcg_at_5=mean_ndcg_at_5,
            configuration=configuration,
            case_results=case_results,
        )

        self.db.add(evaluation_run)
        self.db.commit()
        self.db.refresh(evaluation_run)

        return evaluation_run

    def list_runs(
        self,
        algorithm_version: str | None = None,
        dataset_version: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MatchingEvaluationRun]:
        query = self.db.query(
            MatchingEvaluationRun
        )

        if algorithm_version:
            query = query.filter(
                MatchingEvaluationRun.algorithm_version
                == algorithm_version,
            )

        if dataset_version:
            query = query.filter(
                MatchingEvaluationRun.dataset_version
                == dataset_version,
            )

        return (
            query
            .order_by(
                MatchingEvaluationRun.id.desc()
            )
            .offset(offset)
            .limit(limit)
            .all()
        )
    def get_by_id(
        self,
        run_id: int,
    ) -> MatchingEvaluationRun | None:
        return (
            self.db.query(
                MatchingEvaluationRun
            )
            .filter(
                MatchingEvaluationRun.id == run_id,
            )
            .first()
        )