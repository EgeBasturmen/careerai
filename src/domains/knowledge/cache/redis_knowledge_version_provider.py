from redis import Redis
from redis.exceptions import RedisError

from src.domains.knowledge.cache.base_knowledge_version_provider import (
    KnowledgeVersionProvider,
)


class RedisKnowledgeVersionProvider(
    KnowledgeVersionProvider,
):
    KEY = "knowledge:version"
    DEFAULT_VERSION = 1

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

    def get_version(
        self,
    ) -> int:
        try:
            version = self.redis_client.get(
                self.KEY
            )
        except RedisError:
            return self.DEFAULT_VERSION

        if version is None:
            return self._initialize_version()

        try:
            parsed_version = int(version)
        except (
            TypeError,
            ValueError,
        ):
            return self._reset_version()

        if parsed_version < self.DEFAULT_VERSION:
            return self._reset_version()

        return parsed_version

    def increment_version(
        self,
    ) -> int:
        try:
            version = self.redis_client.incr(
                self.KEY
            )
        except RedisError:
            return self.DEFAULT_VERSION

        parsed_version = int(version)

        if parsed_version < self.DEFAULT_VERSION:
            return self._reset_version()

        return parsed_version

    def _initialize_version(
        self,
    ) -> int:
        try:
            was_created = (
                self.redis_client.set(
                    name=self.KEY,
                    value=self.DEFAULT_VERSION,
                    nx=True,
                )
            )

            if was_created:
                return self.DEFAULT_VERSION

            existing_version = (
                self.redis_client.get(
                    self.KEY
                )
            )

            if existing_version is None:
                return self.DEFAULT_VERSION

            parsed_version = int(
                existing_version
            )

            if (
                parsed_version
                < self.DEFAULT_VERSION
            ):
                return self._reset_version()

            return parsed_version

        except (
            RedisError,
            TypeError,
            ValueError,
        ):
            return self.DEFAULT_VERSION

    def _reset_version(
        self,
    ) -> int:
        try:
            self.redis_client.set(
                name=self.KEY,
                value=self.DEFAULT_VERSION,
            )
        except RedisError:
            return self.DEFAULT_VERSION

        return self.DEFAULT_VERSION