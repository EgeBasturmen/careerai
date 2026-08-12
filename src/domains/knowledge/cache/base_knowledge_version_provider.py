from abc import ABC, abstractmethod


class KnowledgeVersionProvider(ABC):
    @property
    @abstractmethod
    def provider_name(
        self,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_version(
        self,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    def increment_version(
        self,
    ) -> int:
        raise NotImplementedError