from abc import ABC, abstractmethod

from src.domains.knowledge.schemas.knowledge_retrieval_schema import (
    KnowledgeRetrievalResult,
)


class BaseKnowledgeReranker(ABC):
    @property
    @abstractmethod
    def reranker_name(
        self,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def rerank(
        self,
        *,
        query_text: str,
        results: list[KnowledgeRetrievalResult],
        limit: int,
        minimum_score: float = 0.0,
    ) -> list[KnowledgeRetrievalResult]:
        raise NotImplementedError