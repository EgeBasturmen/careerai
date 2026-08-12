from abc import (
    ABC,
    abstractmethod,
)

from src.domains.knowledge.schemas.knowledge_retrieval_schema import (
    KnowledgeRetrievalResult,
)


class BaseKnowledgeRetriever(ABC):
    @property
    @abstractmethod
    def retriever_name(
        self,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError