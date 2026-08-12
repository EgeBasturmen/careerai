from types import SimpleNamespace

import pytest

from src.domains.knowledge.evaluation.dataset_evaluator import (
    DatasetEvaluator,
)
from src.domains.knowledge.evaluation.evaluation_case import (
    EvaluationCase,
)
from src.domains.knowledge.evaluation.evaluation_dataset import (
    EvaluationDataset,
)
from src.domains.knowledge.evaluation.retrieval_evaluator import (
    RetrievalEvaluator,
)


class FakeKnowledgeRetriever:
    def __init__(
        self,
        responses_by_query: dict[
            str,
            list[int],
        ],
    ):
        self.responses_by_query = (
            responses_by_query
        )

    def retrieve(
        self,
        request,
    ):
        document_ids = (
            self.responses_by_query.get(
                request.query,
                [],
            )
        )

        results = [
            SimpleNamespace(
                document_id=document_id,
            )
            for document_id in document_ids
        ]

        return SimpleNamespace(
            results=results,
        )


def test_evaluate_dataset_returns_mean_metrics() -> None:
    retriever = FakeKnowledgeRetriever(
        responses_by_query={
            "python developer": [
                10,
                20,
                30,
            ],
            "machine learning": [
                50,
                60,
                70,
            ],
        }
    )

    evaluator = DatasetEvaluator(
        retriever=retriever,
        retrieval_evaluator=(
            RetrievalEvaluator()
        ),
    )

    dataset = EvaluationDataset(
        dataset_name="careerai-rag",
        version="v1",
        cases=[
            EvaluationCase(
                case_id="case-1",
                query="python developer",
                expected_document_ids=[
                    10,
                    30,
                ],
                category="career",
                language="en",
            ),
            EvaluationCase(
                case_id="case-2",
                query="machine learning",
                expected_document_ids=[
                    50,
                    80,
                ],
                category="career",
                language="en",
            ),
        ],
    )

    report = evaluator.evaluate(
        dataset=dataset,
        k=3,
    )

    assert report.dataset_name == (
        "careerai-rag"
    )

    assert report.version == "v1"
    assert report.case_count == 2

    assert (
        report.mean_precision_at_k
        == pytest.approx(
            0.5,
        )
    )

    assert (
        report.mean_recall_at_k
        == pytest.approx(
            0.75,
        )
    )

    assert report.mean_mrr == pytest.approx(
        1.0
    )

    assert (
        0.0
        < report.mean_ndcg_at_k
        <= 1.0
    )


def test_evaluate_rejects_empty_dataset() -> None:
    retriever = FakeKnowledgeRetriever(
        responses_by_query={},
    )

    evaluator = DatasetEvaluator(
        retriever=retriever,
        retrieval_evaluator=(
            RetrievalEvaluator()
        ),
    )

    dataset = EvaluationDataset(
        dataset_name="careerai-rag",
        version="v1",
        cases=[],
    )

    with pytest.raises(
        ValueError,
        match=(
            "Evaluation dataset must "
            "contain at least one case"
        ),
    ):
        evaluator.evaluate(
            dataset=dataset,
            k=5,
        )


def test_evaluate_rejects_invalid_k() -> None:
    retriever = FakeKnowledgeRetriever(
        responses_by_query={},
    )

    evaluator = DatasetEvaluator(
        retriever=retriever,
        retrieval_evaluator=(
            RetrievalEvaluator()
        ),
    )

    dataset = EvaluationDataset(
        dataset_name="careerai-rag",
        version="v1",
        cases=[
            EvaluationCase(
                case_id="case-1",
                query="python",
                expected_document_ids=[
                    10,
                ],
            ),
        ],
    )

    with pytest.raises(
        ValueError,
        match="k must be greater than zero",
    ):
        evaluator.evaluate(
            dataset=dataset,
            k=0,
        )