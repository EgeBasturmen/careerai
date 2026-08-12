from abc import ABC, abstractmethod


class LLMClient(ABC):
    @property
    @abstractmethod
    def provider_name(
        self,
    ) -> str:
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        prompt_name: str | None = None,
        prompt_version: str | None = None,
    ) -> str:
        pass