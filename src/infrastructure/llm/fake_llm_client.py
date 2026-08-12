from src.infrastructure.llm.base import LLMClient
from src.observability.llm_logger import (
    LLMCallLog,
    LLMLogger,
    now,
)


class FakeLLMClient(LLMClient):
    def __init__(
        self,
    ):
        self.model_name = "fake-llm"
        self.llm_logger = LLMLogger()
    @property
    def provider_name(
        self,
    ) -> str:
        return "fake"

    def generate(
        self,
        prompt: str,
        prompt_name: str | None = None,
        prompt_version: str | None = None,
    ) -> str:
        start_time = now()

        response_text = (
            "This is a fake LLM response. "
            "Real provider integration will be added later."
        )

        latency_ms = (
            now()
            - start_time
        ) * 1000

        self.llm_logger.log(
            LLMCallLog(
                provider="fake",
                model=self.model_name,
                prompt_length=len(prompt),
                prompt_name=prompt_name,
                prompt_version=prompt_version,
                response_length=len(response_text),
                success=True,
                latency_ms=latency_ms,
            )
        )

        return response_text