import pytest

from src.domains.knowledge.evaluation.answer.citation_coverage_evaluator import (
    CitationCoverageEvaluator,
)


def test_returns_full_score_for_valid_citations(
) -> None:
    evaluator = (
        CitationCoverageEvaluator()
    )

    result = evaluator.evaluate(
        question="What is FastAPI?",
        answer=(
            "FastAPI is a Python web "
            "framework [Source 1]."
        ),
        retrieved_context=(
            "[Source 1]\n"
            "FastAPI is a modern Python "
            "web framework.\n\n"
            "[Source 2]\n"
            "It supports type hints."
        ),
    )

    assert result.evaluator_name == (
        "citation_coverage"
    )
    assert result.score == 1.0
    assert result.passed is True
    assert result.explanation == (
        "All answer citations reference "
        "sources available in the "
        "retrieved context."
    )


def test_returns_zero_when_answer_has_no_citations(
) -> None:
    evaluator = (
        CitationCoverageEvaluator()
    )

    result = evaluator.evaluate(
        question="What is FastAPI?",
        answer=(
            "FastAPI is a Python web "
            "framework."
        ),
        retrieved_context=(
            "[Source 1]\n"
            "FastAPI is a modern Python "
            "web framework."
        ),
    )

    assert result.score == 0.0
    assert result.passed is False
    assert result.explanation == (
        "Answer contains no source "
        "citations."
    )


def test_returns_zero_when_context_has_no_sources(
) -> None:
    evaluator = (
        CitationCoverageEvaluator()
    )

    result = evaluator.evaluate(
        question="What is FastAPI?",
        answer=(
            "FastAPI is a framework "
            "[Source 1]."
        ),
        retrieved_context=(
            "FastAPI is a modern Python "
            "web framework."
        ),
    )

    assert result.score == 0.0
    assert result.passed is False
    assert result.explanation == (
        "Retrieved context contains "
        "no identifiable sources."
    )


def test_returns_partial_score_for_unknown_source(
) -> None:
    evaluator = (
        CitationCoverageEvaluator()
    )

    result = evaluator.evaluate(
        question="What is FastAPI?",
        answer=(
            "FastAPI is fast [Source 1]. "
            "It is written in Java "
            "[Source 3]."
        ),
        retrieved_context=(
            "[Source 1]\n"
            "FastAPI is a Python framework.\n\n"
            "[Source 2]\n"
            "FastAPI supports type hints."
        ),
    )

    assert result.score == 0.5
    assert result.passed is False
    assert result.explanation == (
        "Answer references unknown "
        "sources: 3."
    )


def test_duplicate_citations_are_counted_once(
) -> None:
    evaluator = (
        CitationCoverageEvaluator()
    )

    result = evaluator.evaluate(
        question="What is FastAPI?",
        answer=(
            "FastAPI is modern [Source 1]. "
            "It is also fast [Source 1]."
        ),
        retrieved_context=(
            "[Source 1]\n"
            "FastAPI is a modern framework."
        ),
    )

    assert result.score == 1.0
    assert result.passed is True


def test_source_matching_is_case_insensitive(
) -> None:
    evaluator = (
        CitationCoverageEvaluator()
    )

    result = evaluator.evaluate(
        question="Question",
        answer="Answer [source 1].",
        retrieved_context=(
            "[SOURCE 1]\nContext"
        ),
    )

    assert result.score == 1.0
    assert result.passed is True


@pytest.mark.parametrize(
    "pass_threshold",
    [
        -0.1,
        1.1,
    ],
)
def test_rejects_invalid_pass_threshold(
    pass_threshold: float,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Pass threshold must be "
            "between 0.0 and 1.0"
        ),
    ):
        CitationCoverageEvaluator(
            pass_threshold=pass_threshold,
        )