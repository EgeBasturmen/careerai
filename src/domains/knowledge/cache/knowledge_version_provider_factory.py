from src.domains.knowledge.cache.base_knowledge_version_provider import (
    KnowledgeVersionProvider,
)
from src.domains.knowledge.cache.redis_knowledge_version_provider import (
    RedisKnowledgeVersionProvider,
)
from src.infrastructure.cache.redis_client import (
    get_redis_client,
)


def get_knowledge_version_provider(
) -> KnowledgeVersionProvider:
    return RedisKnowledgeVersionProvider(
        redis_client=get_redis_client(),
    )