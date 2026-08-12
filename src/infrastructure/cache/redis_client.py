from functools import lru_cache

from redis import Redis

from src.core.config.settings import settings


@lru_cache
def get_redis_client() -> Redis:
    return Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=(
            settings
            .knowledge_retrieval_cache_redis_db
        ),
        decode_responses=True,
        socket_connect_timeout=1,
        socket_timeout=1,
        health_check_interval=30,
    )