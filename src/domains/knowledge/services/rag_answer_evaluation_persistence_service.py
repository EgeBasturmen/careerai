from sqlalchemy.orm import Session

from src.domains.knowledge.evaluation.answer.answer_evaluation_report import (
    AnswerEvaluationReport,
)
from src.domains.knowledge.models.rag_answer_evaluation import (
    RAGAnswerEvaluation,
)
from src.domains.knowledge.repositories.rag_answer_evaluation_repository import (
    RAGAnswerEvaluationRepository,
)


class RAGAnswerEvaluationPersistenceService:
    DEFAULT_EVALUATION_PROFILE = "default"
    DEFAULT_EVALUATOR_VERSION = "v1"

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db
        self.repository = (
            RAGAnswerEvaluationRepository(db)
        )

    def save(
        self,
        *,
        rag_run_id: int,
        report: AnswerEvaluationReport,
        evaluation_profile: str = (
            DEFAULT_EVALUATION_PROFILE
        ),
        evaluator_version: str = (
            DEFAULT_EVALUATOR_VERSION
        ),
        judge_provider: str | None = None,
        judge_model: str | None = None,
    ) -> RAGAnswerEvaluation:
        evaluation = RAGAnswerEvaluation(
            rag_run_id=rag_run_id,
            overall_score=report.overall_score,
            passed=report.passed,
            evaluator_count=(
                report.evaluator_count
            ),
            failed_evaluator_names=list(
                report.failed_evaluator_names
            ),
            results=[
                result.to_dict()
                for result in report.results
            ],
            evaluation_profile=(
                evaluation_profile
            ),
            evaluator_version=(
                evaluator_version
            ),
            judge_provider=judge_provider,
            judge_model=judge_model,
        )

        try:
            saved_evaluation = (
                self.repository.add(
                    evaluation
                )
            )

            self.db.commit()
            self.db.refresh(
                saved_evaluation
            )

            return saved_evaluation

        except Exception:
            self.db.rollback()
            raise