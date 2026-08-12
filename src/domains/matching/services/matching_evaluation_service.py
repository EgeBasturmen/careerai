from sqlalchemy.orm import Session

from src.domains.matching.evaluation.dataset_loader import (
    MatchingEvaluationDatasetLoader,
)
from src.domains.matching.evaluation.evaluator import (
    MatchingEvaluator,
)
from src.domains.matching.repositories.matching_evaluation_run_repository import (
    MatchingEvaluationRunRepository,
)
from dataclasses import asdict

class MatchingEvaluationService:

    def __init__(
        self,
        db: Session,
    ):
        self.repository = (
            MatchingEvaluationRunRepository(
                db
            )
        )

        self.loader = (
            MatchingEvaluationDatasetLoader()
        )

        self.evaluator = (
            MatchingEvaluator(db)
        )


    def run(
        self,
        dataset_path: str,
    ):

        dataset = self.loader.load(
            dataset_path
        )

        result = self.evaluator.evaluate(
            dataset=dataset
        )

        saved_run = self.repository.create(
            dataset_name=(
                result.dataset_name
            ),
            dataset_version=(
                result.dataset_version
            ),
            algorithm_version=(
                result.algorithm_version
            ),
            case_count=(
                result.case_count
            ),
            mean_precision_at_5=(
                result.mean_precision_at_5
            ),
            mean_recall_at_5=(
                result.mean_recall_at_5
            ),
            mean_reciprocal_rank=(
                result.mean_reciprocal_rank
            ),
            mean_ndcg_at_5=(
                result.mean_ndcg_at_5
            ),
            configuration=(
                result.configuration
            ),
            case_results=[
                asdict(case)
                for case in result.cases
            ],
        )

        return saved_run