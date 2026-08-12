from math import log2

from src.domains.knowledge.evaluation.retrieval_metrics import (
    RetrievalMetrics,
)


class RetrievalEvaluator:
    def evaluate(
        self,
        *,
        retrieved_document_ids: list[int],
        relevant_document_ids: set[int],
        k: int,
    ) -> RetrievalMetrics:
        if k <= 0:
            raise ValueError(
                "k must be greater than zero"
            )

        ranked_document_ids = (
            self.deduplicate_preserving_order(
                retrieved_document_ids
            )[:k]
        )

        unique_relevant_document_ids = set(
            relevant_document_ids
        )

        relevant_retrieved_count = sum(
            1
            for document_id
            in ranked_document_ids
            if document_id
            in unique_relevant_document_ids
        )

        precision_at_k = (
            relevant_retrieved_count
            / len(ranked_document_ids)
            if ranked_document_ids
            else 0.0
        )

        recall_at_k = (
            relevant_retrieved_count
            / len(
                unique_relevant_document_ids
            )
            if unique_relevant_document_ids
            else 0.0
        )

        mrr = self._calculate_mrr(
            ranked_document_ids=(
                ranked_document_ids
            ),
            relevant_document_ids=(
                unique_relevant_document_ids
            ),
        )

        ndcg_at_k = self._calculate_ndcg_at_k(
            ranked_document_ids=(
                ranked_document_ids
            ),
            relevant_document_ids=(
                unique_relevant_document_ids
            ),
            k=k,
        )

        return RetrievalMetrics(
            precision_at_k=precision_at_k,
            recall_at_k=recall_at_k,
            mrr=mrr,
            ndcg_at_k=ndcg_at_k,
            retrieved_count=len(
                ranked_document_ids
            ),
            relevant_count=len(
                unique_relevant_document_ids
            ),
            relevant_retrieved_count=(
                relevant_retrieved_count
            ),
        )

    def _calculate_mrr(
        self,
        *,
        ranked_document_ids: list[int],
        relevant_document_ids: set[int],
    ) -> float:
        for rank, document_id in enumerate(
            ranked_document_ids,
            start=1,
        ):
            if (
                document_id
                in relevant_document_ids
            ):
                return 1.0 / rank

        return 0.0

    def _calculate_ndcg_at_k(
        self,
        *,
        ranked_document_ids: list[int],
        relevant_document_ids: set[int],
        k: int,
    ) -> float:
        dcg = self._calculate_dcg(
            ranked_document_ids=(
                ranked_document_ids
            ),
            relevant_document_ids=(
                relevant_document_ids
            ),
        )

        ideal_relevant_count = min(
            len(relevant_document_ids),
            k,
        )

        if ideal_relevant_count == 0:
            return 0.0

        ideal_ranked_document_ids = list(
            range(ideal_relevant_count)
        )

        ideal_relevant_document_ids = set(
            ideal_ranked_document_ids
        )

        idcg = self._calculate_dcg(
            ranked_document_ids=(
                ideal_ranked_document_ids
            ),
            relevant_document_ids=(
                ideal_relevant_document_ids
            ),
        )

        if idcg == 0.0:
            return 0.0

        return dcg / idcg

    def _calculate_dcg(
        self,
        *,
        ranked_document_ids: list[int],
        relevant_document_ids: set[int],
    ) -> float:
        dcg = 0.0

        for rank, document_id in enumerate(
            ranked_document_ids,
            start=1,
        ):
            relevance = (
                1.0
                if document_id
                in relevant_document_ids
                else 0.0
            )

            if relevance == 0.0:
                continue

            dcg += (
                relevance
                / log2(rank + 1)
            )

        return dcg
    
    def deduplicate_preserving_order(
        self,
        document_ids: list[int],
    ) -> list[int]:
        seen_document_ids: set[int] = set()
        unique_document_ids: list[int] = []

        for document_id in document_ids:
            if document_id in seen_document_ids:
                continue

            seen_document_ids.add(
                document_id
            )

            unique_document_ids.append(
                document_id
            )

        return unique_document_ids