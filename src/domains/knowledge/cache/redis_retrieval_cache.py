from redis import Redis
from redis.exceptions import RedisError

from src.domains.knowledge.cache.base_retrieval_cache import (
    RetrievalCache,
)
from src.domains.knowledge.schemas.knowledge_retrieval_schema import (
    KnowledgeSearchResponse,
)


class RedisRetrievalCache(
    RetrievalCache,
):
    KEY_PREFIX = "knowledge:retrieval:"

    def __init__(
        self,
        redis_client: Redis,
    ) -> None:
        self.redis_client = redis_client

    @property
    def provider_name(
        self,
    ) -> str:
        return "redis"

    def get(
        self,
        key: str,
    ) -> KnowledgeSearchResponse | None:
        try:
            cached_value = self.redis_client.get(
                key
            )
        except RedisError:
            return None

        if cached_value is None:
            return None

        try:
            return (
                KnowledgeSearchResponse
                .model_validate_json(
                    cached_value
                )
            )
        except (
            ValueError,
            TypeError,
        ):
            self.delete(key)
            return None

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

        serialized_value = (
            value.model_dump_json()
        )

        try:
            self.redis_client.set(
                name=key,
                value=serialized_value,
                ex=ttl_seconds,
            )
        except RedisError:
            return

    def delete(
        self,
        key: str,
    ) -> None:
        try:
            self.redis_client.delete(
                key
            )
        except RedisError:
            return

    def clear(self) -> None:
        try:
            keys = list(
                self.redis_client.scan_iter(
                    match=(
                        f"{self.KEY_PREFIX}*"
                    )
                )
            )

            if keys:
                self.redis_client.delete(
                    *keys
                )
        except RedisError:
            return