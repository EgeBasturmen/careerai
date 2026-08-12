import time

from src.domains.knowledge.cache.base_retrieval_cache import (
    RetrievalCache,
)
from src.domains.knowledge.schemas.knowledge_retrieval_schema import (
    KnowledgeSearchResponse,
)


class MemoryRetrievalCache(
    RetrievalCache,
):
    def __init__(self):
        self._cache: dict[
            str,
            tuple[
                float,
                KnowledgeSearchResponse,
            ],
        ] = {}

    @property
    def provider_name(
        self,
    ) -> str:
        return "memory"

    def get(
        self,
        key: str,
    ) -> KnowledgeSearchResponse | None:
        entry = self._cache.get(
            key
        )

        if entry is None:
            return None

        expires_at, value = entry

        if expires_at <= time.time():
            del self._cache[key]
            return None

        return value

    def set(
        self,
        key: str,
        value: KnowledgeSearchResponse,
        ttl_seconds: int,
    ) -> None:
        if ttl_seconds <= 0:
            raise ValueError(
                "ttl_seconds must be "
                "greater than zero"
            )

        self._cache[key] = (
            time.time() + ttl_seconds,
            value,
        )

    def delete(
        self,
        key: str,
    ) -> None:
        self._cache.pop(
            key,
            None,
        )

    def clear(self) -> None:
        self._cache.clear()

