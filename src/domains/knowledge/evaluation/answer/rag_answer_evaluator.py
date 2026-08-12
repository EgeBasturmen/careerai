from src.domains.knowledge.evaluation.answer.answer_evaluation_context import (
    AnswerEvaluationContext,
)
from src.domains.knowledge.evaluation.answer.answer_evaluation_report import (
    AnswerEvaluationReport,
)
from src.domains.knowledge.evaluation.answer.base_answer_evaluator import (
    BaseAnswerEvaluator,
)


class RAGAnswerEvaluator:
    def __init__(
        self,
        evaluators: tuple[
            BaseAnswerEvaluator,
            ...,
        ],
    ) -> None:
        if not evaluators:
            raise ValueError(
                "At least one evaluator is required"
            )

        self.evaluators = evaluators

    def evaluate(
        self,
        *,
        evaluation_context: (
            AnswerEvaluationContext
        ),
    ) -> AnswerEvaluationReport:
        results = []

        for evaluator in self.evaluators:
            result = evaluator.evaluate(
                evaluation_context=(
                    evaluation_context
                ),
            )

            results.append(result)

        return AnswerEvaluationReport(
            results=tuple(results),
        )