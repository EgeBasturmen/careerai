from collections.abc import Sequence

from src.domains.knowledge.rerankers.base import (
    BaseKnowledgeReranker,
)
from src.domains.knowledge.schemas.knowledge_retrieval_schema import (
    KnowledgeRetrievalResult,
)
from src.infrastructure.reranking.cross_encoder_scorer import (
    CrossEncoderScorer,
)


class CrossEncoderKnowledgeReranker(
    BaseKnowledgeReranker,
):
    def __init__(
        self,
        *,
        model_name: str,
        batch_size: int = 16,
    ) -> None:
        self.scorer = CrossEncoderScorer(
            model_name=model_name,
            batch_size=batch_size,
        )

        self.model_name = (
            self.scorer.model_name
        )

        self.batch_size = (
            self.scorer.batch_size
        )

    @property
    def reranker_name(
        self,
    ) -> str:
        return "cross_encoder"

    def rerank(
        self,
        *,
        query_text: str,
        results: list[
            KnowledgeRetrievalResult
        ],
        limit: int,
        minimum_score: float = 0.0,
    ) -> list[KnowledgeRetrievalResult]:
        normalized_query = (
            query_text.strip()
        )

        if not normalized_query:
            raise ValueError(
                "Reranker query cannot be empty"
            )

        if limit < 1:
            raise ValueError(
                "Reranker limit must be positive"
            )

        if not results:
            return []

        passages = [
            self._build_passage(result)
            for result in results
        ]

        predicted_scores = (
            self.scorer.score(
                query_text=normalized_query,
                passages=passages,
            )
        )

        scored_results = [
            (
                result,
                float(score),
                original_rank,
            )
            for original_rank, (
                result,
                score,
            ) in enumerate(
                zip(
                    results,
                    predicted_scores,
                    strict=True,
                ),
                start=1,
            )
        ]

        scored_results.sort(
            key=lambda item: (
                item[1],
                -item[2],
            ),
            reverse=True,
        )

        reranked_results: list[
            KnowledgeRetrievalResult
        ] = []

        for (
            result,
            reranker_score,
            original_rank,
        ) in scored_results:
            if (
                reranker_score
                < minimum_score
            ):
                continue

            chunk_metadata = dict(
                result.chunk_metadata
            )

            chunk_metadata.update(
                {
                    "retrieval_score": (
                        result.similarity_score
                    ),
                    "retrieval_rank": (
                        original_rank
                    ),
                    "reranker": (
                        self.reranker_name
                    ),
                    "reranker_model_name": (
                        self.model_name
                    ),
                    "reranker_score": (
                        reranker_score
                    ),
                }
            )

            reranked_results.append(
                result.model_copy(
                    update={
                        "similarity_score": (
                            reranker_score
                        ),
                        "chunk_metadata": (
                            chunk_metadata
                        ),
                    }
                )
            )

            if (
                len(reranked_results)
                >= limit
            ):
                break

        return reranked_results

    def _build_passage(
        self,
        result: KnowledgeRetrievalResult,
    ) -> str:
        values: Sequence[str | None] = (
            result.document_title,
            result.category,
            result.content,
        )

        return "\n".join(
            value.strip()
            for value in values
            if value and value.strip()
        )