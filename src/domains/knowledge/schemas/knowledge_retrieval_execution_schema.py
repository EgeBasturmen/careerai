from dataclasses import dataclass

from src.domains.knowledge.schemas.knowledge_retrieval_schema import (
    KnowledgeSearchResponse,
)


@dataclass(
    frozen=True,
    slots=True,
)
class KnowledgeRetrievalExecution:
    response: KnowledgeSearchResponse

    cache_enabled: bool
    cache_hit: bool | None
    cache_provider: str | None

    cache_read_latency_ms: float | None
    cache_write_latency_ms: float | None