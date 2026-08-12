import hashlib

from src.domains.knowledge.cache.base_knowledge_version_provider import (
    KnowledgeVersionProvider,
)
from src.domains.knowledge.cache.knowledge_version_provider_factory import (
    get_knowledge_version_provider,
)
from src.domains.knowledge.schemas.knowledge_retrieval_schema import (
    KnowledgeSearchRequest,
)


class RetrievalCacheKeyBuilder:
    def __init__(
        self,
        version_provider: (
            KnowledgeVersionProvider | None
        ) = None,
    ) -> None:
        self.version_provider = (
            version_provider
            or get_knowledge_version_provider()
        )

    def build(
        self,
        request: KnowledgeSearchRequest,
    ) -> str:
        knowledge_version = (
            self.version_provider
            .get_version()
        )

        payload = (
            f"{knowledge_version}|"
            f"{request.query}|"
            f"{request.limit}|"
            f"{request.minimum_similarity}|"
            f"{request.category}|"
            f"{request.language}"
        )

        digest = hashlib.sha256(
            payload.encode("utf-8")
        ).hexdigest()

        return (
            f"knowledge:retrieval:"
            f"{knowledge_version}:"
            f"{digest}"
        )