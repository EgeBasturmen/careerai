from src.domains.knowledge.cache.base_retrieval_cache import (
    RetrievalCache,
)
from src.domains.knowledge.cache.redis_retrieval_cache import (
    RedisRetrievalCache,
)
from src.infrastructure.cache.redis_client import (
    get_redis_client,
)


def get_retrieval_cache() -> RetrievalCache:
    return RedisRetrievalCache(
        redis_client=get_redis_client(),
    )