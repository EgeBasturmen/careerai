from dataclasses import dataclass
from types import SimpleNamespace

from sqlalchemy.orm import Session

from src.domains.matching.evaluation.dataset_loader import (
    MatchingEvaluationDataset,
)
from src.domains.matching.evaluation.metrics import (
    RankingMetrics,
)
from src.domains.matching.services.matching_service import (
    MatchingService,
)


@dataclass(slots=True)
class MatchingCaseEvaluationResult:
    case_name: str
    resume_id: int

    precision_at_5: float
    recall_at_5: float
    reciprocal_rank: float
    ndcg_at_5: float

    predicted_job_ids: list[int]


@dataclass(slots=True)
class MatchingEvaluationResult:
    dataset_name: str
    dataset_version: str
    algorithm_version: str

    case_count: int

    mean_precision_at_5: float
    mean_recall_at_5: float
    mean_reciprocal_rank: float
    mean_ndcg_at_5: float
    configuration: dict

    cases: list[
        MatchingCaseEvaluationResult
    ]


class MatchingEvaluator:
    def __init__(
        self,
        db: Session,
    ):
        self.matching_service = (
            MatchingService(db)
        )

        self.metrics = RankingMetrics()

    def evaluate(
        self,
        dataset: MatchingEvaluationDataset,
        matching_configuration: dict = {}
    ) -> MatchingEvaluationResult:
        case_results: list[
            MatchingCaseEvaluationResult
        ] = []

        algorithm_version = "unknown"

        for case in dataset.cases:
            current_user = SimpleNamespace(
                id=case.user_id,
            )

            response = (
                self.matching_service
                .match_resume_to_jobs(
                    current_user=current_user,
                    resume_id=case.resume_id,
                    limit=100,
                    offset=0,
                    candidate_limit=500,
                    minimum_similarity=0.0,
                )
            )
            matching_configuration = (
                response.configuration.model_dump()
            )

            algorithm_version = (
                response
                .configuration
                .algorithm_version
            )

            predicted_job_ids = [
                match.job_id
                for match in response.matches
            ]

            relevant_job_ids = {
                job_id
                for job_id, grade
                in case.relevance_grades.items()
                if grade > 0
            }

            case_results.append(
                MatchingCaseEvaluationResult(
                    case_name=case.name,
                    resume_id=case.resume_id,
                    precision_at_5=(
                        self.metrics
                        .precision_at_k(
                            predicted_job_ids=(
                                predicted_job_ids
                            ),
                            relevant_job_ids=(
                                relevant_job_ids
                            ),
                            k=5,
                        )
                    ),
                    recall_at_5=(
                        self.metrics
                        .recall_at_k(
                            predicted_job_ids=(
                                predicted_job_ids
                            ),
                            relevant_job_ids=(
                                relevant_job_ids
                            ),
                            k=5,
                        )
                    ),
                    reciprocal_rank=(
                        self.metrics
                        .reciprocal_rank(
                            predicted_job_ids=(
                                predicted_job_ids
                            ),
                            relevant_job_ids=(
                                relevant_job_ids
                            ),
                        )
                    ),
                    ndcg_at_5=(
                        self.metrics
                        .ndcg_at_k(
                            predicted_job_ids=(
                                predicted_job_ids
                            ),
                            relevance_grades=(
                                case.relevance_grades
                            ),
                            k=5,
                        )
                    ),
                    predicted_job_ids=(
                        predicted_job_ids[:10]
                    ),
                )
            )

        return MatchingEvaluationResult(
            dataset_name=dataset.dataset_name,
            dataset_version=(
                dataset.dataset_version
            ),
            algorithm_version=(
                algorithm_version
            ),
            case_count=len(case_results),
            mean_precision_at_5=(
                self._mean(
                    result.precision_at_5
                    for result in case_results
                )
            ),
            mean_recall_at_5=(
                self._mean(
                    result.recall_at_5
                    for result in case_results
                )
            ),
            mean_reciprocal_rank=(
                self._mean(
                    result.reciprocal_rank
                    for result in case_results
                )
            ),
            mean_ndcg_at_5=(
                self._mean(
                    result.ndcg_at_5
                    for result in case_results
                )
            ),
            cases=case_results,
            configuration=matching_configuration,
        )

    def _mean(
        self,
        values,
    ) -> float:
        value_list = list(values)

        if not value_list:
            return 0.0

        return sum(value_list) / len(
            value_list
        )