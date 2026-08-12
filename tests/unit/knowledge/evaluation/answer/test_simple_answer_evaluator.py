import pytest

from src.domains.knowledge.evaluation.answer.simple_answer_evaluator import (
    SimpleAnswerEvaluator,
)


def test_returns_success_for_non_empty_answer() -> None:
    evaluator = SimpleAnswerEvaluator()

    result = evaluator.evaluate(
        question="What is FastAPI?",
        answer="FastAPI is a web framework.",
        retrieved_context="FastAPI is a modern Python framework.",
    )

    assert result.score == 1.0
    assert result.passed is True
    assert result.evaluator_name == "simple"


@pytest.mark.parametrize(
    "answer",
    [
        "",
        " ",
        "\n",
        "\t",
    ],
)
def test_returns_failure_for_empty_answer(
    answer: str,
) -> None:
    evaluator = SimpleAnswerEvaluator()

    result = evaluator.evaluate(
        question="Question",
        answer=answer,
        retrieved_context="Context",
    )

    assert result.score == 0.0
    assert result.passed is False