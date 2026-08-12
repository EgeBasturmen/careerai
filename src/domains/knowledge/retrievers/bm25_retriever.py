import re

from rank_bm25 import BM25Plus
from sqlalchemy.orm import Session

from src.domains.knowledge.repositories.knowledge_retrieval_repository import (
    KnowledgeRetrievalRepository,
)
from src.domains.knowledge.retrievers.base import (
    BaseKnowledgeRetriever,
)
from src.domains.knowledge.schemas.knowledge_retrieval_schema import (
    KnowledgeRetrievalCandidate,
    KnowledgeRetrievalResult,
)


class BM25KnowledgeRetriever(
    BaseKnowledgeRetriever,
):
    CANDIDATE_LIMIT = 1000
    ENGLISH_STOP_WORDS = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "how",
        "i",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "should",
        "that",
        "the",
        "this",
        "to",
        "was",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "with",
        "you",
        "your",
    }


    def __init__(
        self,
        db: Session,
    ):
        self.repository = (
            KnowledgeRetrievalRepository(
                db
            )
        )

    @property
    def retriever_name(
        self,
    ) -> str:
        return "bm25"

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
        del query_embedding

        normalized_query = (
            self._normalize_text(
                query_text
            )
        )

        query_tokens = self._tokenize(
            normalized_query
        )

        if not query_tokens:
            return []

        candidates = (
            self.repository.list_candidates(
                category=category,
                language=language,
                candidate_limit=(
                    self.CANDIDATE_LIMIT
                ),
            )
        )

        if not candidates:
            return []

        tokenized_corpus = [
            self._tokenize(
                self._build_candidate_text(
                    candidate
                )
            )
            for candidate in candidates
        ]

        bm25 = BM25Plus(
            tokenized_corpus
        )

        raw_scores = bm25.get_scores(
            query_tokens
        )

        scored_candidates: list[
            tuple[
                KnowledgeRetrievalCandidate,
                float,
            ]
        ] = []

        query_token_set = set(
            query_tokens
        )

        for (
            candidate,
            candidate_tokens,
            raw_score,
        ) in zip(
            candidates,
            tokenized_corpus,
            raw_scores,
            strict=True,
        ):
            candidate_token_set = set(
                candidate_tokens
            )

            has_token_overlap = bool(
                query_token_set
                & candidate_token_set
            )

            if not has_token_overlap:
                continue

            scored_candidates.append(
                (
                    candidate,
                    float(raw_score),
                )
            )

        scored_candidates.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        if not scored_candidates:
            return []

        maximum_score = scored_candidates[
            0
        ][1]

        results: list[
            KnowledgeRetrievalResult
        ] = []

        for candidate, raw_score in (
            scored_candidates
        ):
            normalized_score = (
                self._normalize_score(
                    score=raw_score,
                    maximum_score=(
                        maximum_score
                    ),
                )
            )

            if (
                normalized_score
                < minimum_similarity
            ):
                continue

            results.append(
                self._build_result(
                    candidate=candidate,
                    normalized_score=(
                        normalized_score
                    ),
                    raw_score=raw_score,
                )
            )

            if len(results) >= limit:
                break

        return results

    def _build_candidate_text(
        self,
        candidate: KnowledgeRetrievalCandidate,
    ) -> str:
        title = candidate.document_title

        return " ".join(
            value
            for value in [
                title,
                title,
                candidate.category,
                candidate.content,
            ]
            if value
        )

    def _build_result(
        self,
        *,
        candidate: KnowledgeRetrievalCandidate,
        normalized_score: float,
        raw_score: float,
    ) -> KnowledgeRetrievalResult:
        chunk_metadata = dict(
            candidate.chunk_metadata
        )

        chunk_metadata.update(
            {
                "retriever": "bm25",
                "bm25_raw_score": (
                    raw_score
                ),
            }
        )

        return KnowledgeRetrievalResult(
            chunk_id=candidate.chunk_id,
            document_id=(
                candidate.document_id
            ),
            chunk_index=(
                candidate.chunk_index
            ),
            document_title=(
                candidate.document_title
            ),
            category=candidate.category,
            language=candidate.language,
            content=candidate.content,
            similarity_score=(
                normalized_score
            ),
            source_type=(
                candidate.source_type
            ),
            source_uri=(
                candidate.source_uri
            ),
            document_metadata=(
                candidate.document_metadata
            ),
            chunk_metadata=(
                chunk_metadata
            ),
        )

    def _tokenize(
        self,
        text: str,
    ) -> list[str]:
        normalized_text = (
            self._normalize_text(
                text
            )
        )

        tokens = re.findall(
            r"\b[\w+#.-]+\b",
            normalized_text,
        )

        return [
            token
            for token in tokens
            if (
                len(token) > 1
                and token
                not in self.ENGLISH_STOP_WORDS
            )
        ]

    def _normalize_text(
        self,
        text: str,
    ) -> str:
        return " ".join(
            text
            .strip()
            .lower()
            .split()
        )

    def _normalize_score(
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