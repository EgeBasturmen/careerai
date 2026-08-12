from abc import ABC, abstractmethod

from src.domains.knowledge.evaluation.answer.answer_evaluation_context import (
    AnswerEvaluationContext,
)
from src.domains.knowledge.evaluation.answer.answer_evaluation_result import (
    AnswerEvaluationResult,
)


class BaseAnswerEvaluator(
    ABC,
):
    @property
    @abstractmethod
    def evaluator_name(
        self,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def evaluate(
        self,
        *,
        evaluation_context: (
            AnswerEvaluationContext
        ),
    ) -> AnswerEvaluationResult:
        raise NotImplementedError