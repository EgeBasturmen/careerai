from collections import defaultdict

from sqlalchemy.orm import Session

from src.domains.knowledge.retrievers.base import (
    BaseKnowledgeRetriever,
)
from src.domains.knowledge.retrievers.bm25_retriever import (
    BM25KnowledgeRetriever,
)
from src.domains.knowledge.retrievers.semantic_retriever import (
    SemanticKnowledgeRetriever,
)
from src.domains.knowledge.schemas.knowledge_retrieval_schema import (
    KnowledgeRetrievalResult,
)


class HybridKnowledgeRetriever(
    BaseKnowledgeRetriever,
):
    RRF_K = 60
    CANDIDATE_MULTIPLIER = 3

    def __init__(
        self,
        db: Session,
        embedding_model_name: str,
    ):
        self.semantic_retriever = (
            SemanticKnowledgeRetriever(
                db=db,
                embedding_model_name=(
                    embedding_model_name
                ),
            )
        )

        self.bm25_retriever = (
            BM25KnowledgeRetriever(
                db
            )
        )

    @property
    def retriever_name(
        self,
    ) -> str:
        return "hybrid"

    def retrieve(
        self,
        *,
        query_text: str,
        query_embedding: list[float] | None,
        limit: int,
        minimum_similarity: float,
        category: str | None = None,
        language: str | None = None,
    ) -> list[KnowledgeRetrievalResult]:
        candidate_limit = max(
            limit
            * self.CANDIDATE_MULTIPLIER,
            limit,
        )

        semantic_results = (
            self.semantic_retriever.retrieve(
                query_text=query_text,
                query_embedding=query_embedding,
                limit=candidate_limit,
                minimum_similarity=0.0,
                category=category,
                language=language,
            )
        )

        bm25_results = (
            self.bm25_retriever.retrieve(
                query_text=query_text,
                query_embedding=query_embedding,
                limit=candidate_limit,
                minimum_similarity=0.0,
                category=category,
                language=language,
            )
        )

        return self._fuse_results(
            semantic_results=semantic_results,
            bm25_results=bm25_results,
            limit=limit,
            minimum_similarity=(
                minimum_similarity
            ),
        )

    def _fuse_results(
        self,
        *,
        semantic_results: list[
            KnowledgeRetrievalResult
        ],
        bm25_results: list[
            KnowledgeRetrievalResult
        ],
        limit: int,
        minimum_similarity: float,
    ) -> list[KnowledgeRetrievalResult]:
        rrf_scores: dict[
            int,
            float,
        ] = defaultdict(float)

        result_by_chunk_id: dict[
            int,
            KnowledgeRetrievalResult,
        ] = {}

        semantic_rank_by_chunk_id: dict[
            int,
            int,
        ] = {}

        bm25_rank_by_chunk_id: dict[
            int,
            int,
        ] = {}

        semantic_score_by_chunk_id: dict[
            int,
            float,
        ] = {}

        bm25_score_by_chunk_id: dict[
            int,
            float,
        ] = {}

        for rank, result in enumerate(
            semantic_results,
            start=1,
        ):
            chunk_id = result.chunk_id

            rrf_scores[chunk_id] += (
                self._calculate_rrf_score(
                    rank
                )
            )

            result_by_chunk_id[
                chunk_id
            ] = result

            semantic_rank_by_chunk_id[
                chunk_id
            ] = rank

            semantic_score_by_chunk_id[
                chunk_id
            ] = result.similarity_score

        for rank, result in enumerate(
            bm25_results,
            start=1,
        ):
            chunk_id = result.chunk_id

            rrf_scores[chunk_id] += (
                self._calculate_rrf_score(
                    rank
                )
            )

            result_by_chunk_id.setdefault(
                chunk_id,
                result,
            )

            bm25_rank_by_chunk_id[
                chunk_id
            ] = rank

            bm25_score_by_chunk_id[
                chunk_id
            ] = result.similarity_score

        ranked_chunk_ids = sorted(
            rrf_scores,
            key=lambda chunk_id: (
                rrf_scores[chunk_id]
            ),
            reverse=True,
        )

        if not ranked_chunk_ids:
            return []

        maximum_rrf_score = max(
            rrf_scores.values()
        )

        fused_results: list[
            KnowledgeRetrievalResult
        ] = []

        for chunk_id in ranked_chunk_ids:
            normalized_rrf_score = (
                self._normalize_rrf_score(
                    score=(
                        rrf_scores[
                            chunk_id
                        ]
                    ),
                    maximum_score=(
                        maximum_rrf_score
                    ),
                )
            )

            if (
                normalized_rrf_score
                < minimum_similarity
            ):
                continue

            original_result = (
                result_by_chunk_id[
                    chunk_id
                ]
            )

            chunk_metadata = dict(
                original_result.chunk_metadata
            )

            chunk_metadata.update(
                {
                    "retriever": "hybrid",
                    "rrf_score": (
                        rrf_scores[
                            chunk_id
                        ]
                    ),
                    "semantic_rank": (
                        semantic_rank_by_chunk_id.get(
                            chunk_id
                        )
                    ),
                    "bm25_rank": (
                        bm25_rank_by_chunk_id.get(
                            chunk_id
                        )
                    ),
                    "semantic_score": (
                        semantic_score_by_chunk_id.get(
                            chunk_id
                        )
                    ),
                    "bm25_score": (
                        bm25_score_by_chunk_id.get(
                            chunk_id
                        )
                    ),
                }
            )

            fused_results.append(
                original_result.model_copy(
                    update={
                        "similarity_score": (
                            normalized_rrf_score
                        ),
                        "chunk_metadata": (
                            chunk_metadata
                        ),
                    }
                )
            )

            if len(fused_results) >= limit:
                break

        return fused_results

    def _calculate_rrf_score(
        self,
        rank: int,
    ) -> float:
        return 1.0 / (
            self.RRF_K
            + rank
        )

    def _normalize_rrf_score(
        self,
        *,
        score: float,
        maximum_score: float,
    ) -> float:
        if maximum_score <= 0:
            return 0.0

        return min(
            score / maximum_score,
            1.0,
        )