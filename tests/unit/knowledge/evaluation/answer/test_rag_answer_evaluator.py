from unittest.mock import Mock

from src.domains.knowledge.evaluation.answer.answer_evaluation_result import (
    AnswerEvaluationResult,
)
from src.domains.knowledge.evaluation.answer.rag_answer_evaluator import (
    RAGAnswerEvaluator,
)


def test_runs_all_evaluators() -> None:
    evaluator1 = Mock()
    evaluator2 = Mock()

    evaluator1.evaluate.return_value = (
        AnswerEvaluationResult(
            evaluator_name="first",
            score=1.0,
            passed=True,
            explanation="ok",
        )
    )

    evaluator2.evaluate.return_value = (
        AnswerEvaluationResult(
            evaluator_name="second",
            score=0.5,
            passed=False,
            explanation="partial",
        )
    )

    rag_evaluator = (
        RAGAnswerEvaluator(
            [
                evaluator1,
                evaluator2,
            ],
        )
    )

    results = rag_evaluator.evaluate(
        question="Question",
        answer="Answer",
        retrieved_context="Context",
    )

    assert len(results) == 2

    assert results[0].evaluator_name == (
        "first"
    )

    assert results[1].evaluator_name == (
        "second"
    )

    evaluator1.evaluate.assert_called_once()

    evaluator2.evaluate.assert_called_once()