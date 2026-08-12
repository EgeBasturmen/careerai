from statistics import mean

from src.domains.knowledge.evaluation.evaluation_dataset import (
    EvaluationDataset,
)
from src.domains.knowledge.evaluation.evaluation_report import (
    EvaluationReport,
)
from src.domains.knowledge.evaluation.retrieval_evaluator import (
    RetrievalEvaluator,
)
from src.domains.knowledge.schemas.knowledge_retrieval_schema import (
    KnowledgeSearchRequest,
)
from src.domains.knowledge.services.knowledge_retriever import (
    KnowledgeRetriever,
)


class DatasetEvaluator:
    def __init__(
        self,
        retriever: KnowledgeRetriever,
        retrieval_evaluator: RetrievalEvaluator,
    ):
        self.retriever = retriever
        self.retrieval_evaluator = (
            retrieval_evaluator
        )

    def evaluate(
        self,
        *,
        dataset: EvaluationDataset,
        k: int,
        minimum_similarity: float = 0.0,
    ) -> EvaluationReport:
        if k <= 0:
            raise ValueError(
                "k must be greater than zero"
            )

        if not dataset.cases:
            raise ValueError(
                "Evaluation dataset must contain "
                "at least one case"
            )

        precision_scores: list[float] = []
        recall_scores: list[float] = []
        mrr_scores: list[float] = []
        ndcg_scores: list[float] = []

        for evaluation_case in dataset.cases:
            retrieval_response = (
                self.retriever.retrieve(
                    KnowledgeSearchRequest(
                        query=(
                            evaluation_case.query
                        ),
                        limit=k,
                        minimum_similarity=(
                            minimum_similarity
                        ),
                        category=(
                            evaluation_case.category
                        ),
                        language=(
                            evaluation_case.language
                        ),
                    )
                )
            )

            retrieved_document_ids = [
                result.document_id
                for result
                in retrieval_response.results
            ]

            metrics = (
                self.retrieval_evaluator
                .evaluate(
                    retrieved_document_ids=(
                        retrieved_document_ids
                    ),
                    relevant_document_ids=set(
                        evaluation_case
                        .expected_document_ids
                    ),
                    k=k,
                )
            )

            precision_scores.append(
                metrics.precision_at_k
            )

            recall_scores.append(
                metrics.recall_at_k
            )

            mrr_scores.append(
                metrics.mrr
            )

            ndcg_scores.append(
                metrics.ndcg_at_k
            )

        return EvaluationReport(
            dataset_name=(
                dataset.dataset_name
            ),
            version=dataset.version,
            case_count=len(
                dataset.cases
            ),
            mean_precision_at_k=mean(
                precision_scores
            ),
            mean_recall_at_k=mean(
                recall_scores
            ),
            mean_mrr=mean(
                mrr_scores
            ),
            mean_ndcg_at_k=mean(
                ndcg_scores
            ),
        )