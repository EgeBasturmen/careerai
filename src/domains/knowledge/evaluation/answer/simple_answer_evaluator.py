from src.domains.knowledge.evaluation.answer.answer_evaluation_result import (
    AnswerEvaluationResult,
)
from src.domains.knowledge.evaluation.answer.base_answer_evaluator import (
    BaseAnswerEvaluator,
)


class SimpleAnswerEvaluator(
    BaseAnswerEvaluator,
):
    @property
    def evaluator_name(
        self,
    ) -> str:
        return "simple"

    def evaluate(
        self,
        *,
        question: str,
        answer: str,
        retrieved_context: str,
    ) -> AnswerEvaluationResult:

        if not answer.strip():
            return AnswerEvaluationResult(
                evaluator_name=self.evaluator_name,
                score=0.0,
                passed=False,
                explanation="Answer is empty.",
            )

        return AnswerEvaluationResult(
            evaluator_name=self.evaluator_name,
            score=1.0,
            passed=True,
            explanation="Answer is not empty.",
        )