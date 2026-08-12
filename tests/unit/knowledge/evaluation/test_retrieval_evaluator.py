import pytest

from src.domains.knowledge.evaluation.retrieval_evaluator import (
    RetrievalEvaluator,
)


def test_evaluate_retrieval_metrics() -> None:
    evaluator = RetrievalEvaluator()

    metrics = evaluator.evaluate(
        retrieved_document_ids=[
            10,
            20,
            30,
            40,
            50,
        ],
        relevant_document_ids={
            10,
            30,
            60,
        },
        k=5,
    )

    assert metrics.precision_at_k == pytest.approx(
        0.4
    )

    assert metrics.recall_at_k == pytest.approx(
        2 / 3
    )

    assert metrics.mrr == pytest.approx(
        1.0
    )

    assert metrics.ndcg_at_k > 0.0
    assert metrics.ndcg_at_k <= 1.0

    assert metrics.retrieved_count == 5
    assert metrics.relevant_count == 3

    assert (
        metrics.relevant_retrieved_count
        == 2
    )


def test_evaluate_deduplicates_documents() -> None:
    evaluator = RetrievalEvaluator()

    metrics = evaluator.evaluate(
        retrieved_document_ids=[
            10,
            10,
            20,
            30,
        ],
        relevant_document_ids={
            10,
            30,
        },
        k=3,
    )

    assert metrics.retrieved_count == 3

    assert (
        metrics.relevant_retrieved_count
        == 2
    )

    assert metrics.precision_at_k == pytest.approx(
        2 / 3
    )


def test_evaluate_returns_zero_when_no_results() -> None:
    evaluator = RetrievalEvaluator()

    metrics = evaluator.evaluate(
        retrieved_document_ids=[],
        relevant_document_ids={
            10,
            20,
        },
        k=5,
    )

    assert metrics.precision_at_k == 0.0
    assert metrics.recall_at_k == 0.0
    assert metrics.mrr == 0.0
    assert metrics.ndcg_at_k == 0.0