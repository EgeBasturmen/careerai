from unittest.mock import Mock

import pytest

from src.domains.knowledge.evaluation.answer.faithfulness_evaluator import (
    FaithfulnessEvaluator,
)
from src.infrastructure.llm.base import (
    LLMClient,
)


def test_returns_passed_result_for_faithful_answer(
) -> None:
    llm_client = Mock(
        spec=LLMClient,
    )

    llm_client.generate.return_value = (
        """
        {
          "score": 0.95,
          "explanation": "The answer is supported by the context."
        }
        """
    )

    evaluator = FaithfulnessEvaluator(
        llm_client=llm_client,
        pass_threshold=0.8,
    )

    result = evaluator.evaluate(
        evaluation_context=(
            build_evaluation_context()
        ),
    )

    assert result.evaluator_name == (
        "faithfulness"
    )
    assert result.score == 0.95
    assert result.passed is True
    assert result.explanation == (
        "The answer is supported by "
        "the context."
    )

    llm_client.generate.assert_called_once()

    call_kwargs = (
        llm_client.generate.call_args.kwargs
    )

    assert (
        call_kwargs["prompt_name"]
        == evaluator.PROMPT_NAME
    )

    assert (
        call_kwargs["prompt_version"]
        == evaluator.PROMPT_VERSION
    )

    assert (
        "What is FastAPI?"
        in call_kwargs["prompt"]
    )

    assert (
        "FastAPI is a Python web framework."
        in call_kwargs["prompt"]
    )

    assert (
        "FastAPI is a modern Python web framework."
        in call_kwargs["prompt"]
    )


def test_returns_failed_result_when_score_is_below_threshold(
) -> None:
    llm_client = Mock(
        spec=LLMClient,
    )

    llm_client.generate.return_value = (
        """
        {
          "score": 0.4,
          "explanation": "The answer contains unsupported claims."
        }
        """
    )

    evaluator = FaithfulnessEvaluator(
        llm_client=llm_client,
        pass_threshold=0.8,
    )

    result = evaluator.evaluate(
        question="What is FastAPI?",
        answer="FastAPI is written in Java.",
        retrieved_context=(
            "FastAPI is a Python framework."
        ),
    )

    assert result.evaluator_name == (
        "faithfulness"
    )
    assert result.score == 0.4
    assert result.passed is False
    assert result.explanation == (
        "The answer contains unsupported "
        "claims."
    )


def test_passes_when_score_equals_threshold(
) -> None:
    llm_client = Mock(
        spec=LLMClient,
    )

    llm_client.generate.return_value = (
        """
        {
          "score": 0.8,
          "explanation": "The answer meets the threshold."
        }
        """
    )

    evaluator = FaithfulnessEvaluator(
        llm_client=llm_client,
        pass_threshold=0.8,
    )

    result = evaluator.evaluate(
        question="Question",
        answer="Answer",
        retrieved_context="Context",
    )

    assert result.score == 0.8
    assert result.passed is True


def test_accepts_json_inside_json_code_fence(
) -> None:
    llm_client = Mock(
        spec=LLMClient,
    )

    llm_client.generate.return_value = (
        """```json
{
  "score": 1.0,
  "explanation": "All claims are supported."
}
```"""
    )

    evaluator = FaithfulnessEvaluator(
        llm_client=llm_client,
    )

    result = evaluator.evaluate(
        question="Question",
        answer="Supported answer",
        retrieved_context="Supporting context",
    )

    assert result.score == 1.0
    assert result.passed is True
    assert result.explanation == (
        "All claims are supported."
    )


def test_accepts_json_inside_plain_code_fence(
) -> None:
    llm_client = Mock(
        spec=LLMClient,
    )

    llm_client.generate.return_value = (
        """```
{
  "score": 0.9,
  "explanation": "The answer is grounded."
}
```"""
    )

    evaluator = FaithfulnessEvaluator(
        llm_client=llm_client,
    )

    result = evaluator.evaluate(
        question="Question",
        answer="Answer",
        retrieved_context="Context",
    )

    assert result.score == 0.9
    assert result.passed is True


def test_raises_error_for_invalid_json(
) -> None:
    llm_client = Mock(
        spec=LLMClient,
    )

    llm_client.generate.return_value = (
        "This is not JSON."
    )

    evaluator = FaithfulnessEvaluator(
        llm_client=llm_client,
    )

    with pytest.raises(
        ValueError,
        match=(
            "Faithfulness judge returned "
            "invalid JSON"
        ),
    ):
        evaluator.evaluate(
            question="Question",
            answer="Answer",
            retrieved_context="Context",
        )


def test_raises_error_when_response_is_not_json_object(
) -> None:
    llm_client = Mock(
        spec=LLMClient,
    )

    llm_client.generate.return_value = (
        '[{"score": 1.0}]'
    )

    evaluator = FaithfulnessEvaluator(
        llm_client=llm_client,
    )

    with pytest.raises(
        ValueError,
        match=(
            "Faithfulness judge response "
            "must be a JSON object"
        ),
    ):
        evaluator.evaluate(
            question="Question",
            answer="Answer",
            retrieved_context="Context",
        )


@pytest.mark.parametrize(
    "response",
    [
        (
            '{"score": 1.5, '
            '"explanation": "Invalid"}'
        ),
        (
            '{"score": -0.1, '
            '"explanation": "Invalid"}'
        ),
        (
            '{"score": "high", '
            '"explanation": "Invalid"}'
        ),
        (
            '{"score": true, '
            '"explanation": "Invalid"}'
        ),
        (
            '{"explanation": "Missing score"}'
        ),
    ],
)
def test_rejects_invalid_scores(
    response: str,
) -> None:
    llm_client = Mock(
        spec=LLMClient,
    )

    llm_client.generate.return_value = (
        response
    )

    evaluator = FaithfulnessEvaluator(
        llm_client=llm_client,
    )

    with pytest.raises(
        ValueError,
        match="Faithfulness score",
    ):
        evaluator.evaluate(
            question="Question",
            answer="Answer",
            retrieved_context="Context",
        )


@pytest.mark.parametrize(
    "response",
    [
        (
            '{"score": 0.9, '
            '"explanation": ""}'
        ),
        (
            '{"score": 0.9, '
            '"explanation": "   "}'
        ),
        '{"score": 0.9}',
        (
            '{"score": 0.9, '
            '"explanation": 123}'
        ),
    ],
)
def test_rejects_invalid_explanation(
    response: str,
) -> None:
    llm_client = Mock(
        spec=LLMClient,
    )

    llm_client.generate.return_value = (
        response
    )

    evaluator = FaithfulnessEvaluator(
        llm_client=llm_client,
    )

    with pytest.raises(
        ValueError,
        match=(
            "Faithfulness explanation "
            "cannot be empty"
        ),
    ):
        evaluator.evaluate(
            question="Question",
            answer="Answer",
            retrieved_context="Context",
        )


@pytest.mark.parametrize(
    (
        "question",
        "answer",
        "retrieved_context",
        "expected_message",
    ),
    [
        (
            "",
            "Answer",
            "Context",
            "Question cannot be empty",
        ),
        (
            "   ",
            "Answer",
            "Context",
            "Question cannot be empty",
        ),
        (
            "Question",
            "",
            "Context",
            "Answer cannot be empty",
        ),
        (
            "Question",
            "   ",
            "Context",
            "Answer cannot be empty",
        ),
        (
            "Question",
            "Answer",
            "",
            (
                "Retrieved context "
                "cannot be empty"
            ),
        ),
        (
            "Question",
            "Answer",
            "   ",
            (
                "Retrieved context "
                "cannot be empty"
            ),
        ),
    ],
)
def test_rejects_empty_inputs(
    question: str,
    answer: str,
    retrieved_context: str,
    expected_message: str,
) -> None:
    llm_client = Mock(
        spec=LLMClient,
    )

    evaluator = FaithfulnessEvaluator(
        llm_client=llm_client,
    )

    with pytest.raises(
        ValueError,
        match=expected_message,
    ):
        evaluator.evaluate(
            question=question,
            answer=answer,
            retrieved_context=(
                retrieved_context
            ),
        )

    llm_client.generate.assert_not_called()


@pytest.mark.parametrize(
    "pass_threshold",
    [
        -0.1,
        1.1,
    ],
)
def test_rejects_invalid_threshold(
    pass_threshold: float,
) -> None:
    llm_client = Mock(
        spec=LLMClient,
    )

    with pytest.raises(
        ValueError,
        match=(
            "Pass threshold must be "
            "between 0.0 and 1.0"
        ),
    ):
        FaithfulnessEvaluator(
            llm_client=llm_client,
            pass_threshold=pass_threshold,
        )