from src.domains.knowledge.evaluation.answer.answer_evaluation_context import (
    AnswerEvaluationContext,
)
from src.domains.knowledge.evaluation.answer.answer_evaluation_report import (
    AnswerEvaluationReport,
)
from src.domains.knowledge.evaluation.answer.rag_answer_evaluator import (
    RAGAnswerEvaluator,
)
from src.domains.knowledge.rag.rag_context import (
    RAGContext,
)
from src.domains.knowledge.rag.rag_generation_result import (
    RAGGenerationResult,
)
from src.domains.knowledge.rag.rag_source_validator import (
    RAGSourceValidationResult,
)


class AnswerEvaluationService:
    def __init__(
        self,
        answer_evaluator: RAGAnswerEvaluator,
    ) -> None:
        self.answer_evaluator = answer_evaluator

    def evaluate(
        self,
        *,
        question: str,
        generation_result: RAGGenerationResult,
        rag_context: RAGContext,
        source_validation_result: (
            RAGSourceValidationResult
        ),
    ) -> AnswerEvaluationReport:
        evaluation_context = (
            AnswerEvaluationContext(
                question=question,
                generation_result=(
                    generation_result
                ),
                rag_context=rag_context,
                source_validation_result=(
                    source_validation_result
                ),
            )
        )

        return self.answer_evaluator.evaluate(
            evaluation_context=(
                evaluation_context
            ),
        )