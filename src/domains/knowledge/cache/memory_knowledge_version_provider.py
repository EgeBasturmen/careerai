from threading import Lock

from src.domains.knowledge.cache.base_knowledge_version_provider import (
    KnowledgeVersionProvider,
)


class MemoryKnowledgeVersionProvider(
    KnowledgeVersionProvider,
):
    DEFAULT_VERSION = 1

    def __init__(
        self,
        initial_version: int = DEFAULT_VERSION,
    ) -> None:
        if initial_version < 1:
            raise ValueError(
                "initial_version must be "
                "greater than or equal to 1"
            )

        self._version = initial_version
        self._lock = Lock()

    @property
    def provider_name(
        self,
    ) -> str:
        return "memory"

    def get_version(
        self,
    ) -> int:
        with self._lock:
            return self._version

    def increment_version(
        self,
    ) -> int:
        with self._lock:
            self._version += 1

            return self._version