from abc import ABC, abstractmethod

from src.domains.knowledge.schemas.knowledge_retrieval_schema import (
    KnowledgeSearchResponse,
)


class RetrievalCache(ABC):
    @property
    @abstractmethod
    def provider_name(
        self,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        key: str,
    ) -> KnowledgeSearchResponse | None:
        raise NotImplementedError

    @abstractmethod
    def set(
        self,
        key: str,
        value: KnowledgeSearchResponse,
        ttl_seconds: int,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        key: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def clear(
        self,
    ) -> None:
        raise NotImplementedError