import google.generativeai as genai

from src.core.config.settings import settings
from src.infrastructure.llm.base import LLMClient
from src.observability.llm_logger import (
    LLMCallLog,
    LLMLogger,
    now,
)
import time

class GeminiLLMClient(LLMClient):
    def __init__(
        self,
    ):
        if not settings.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured"
            )

        genai.configure(
            api_key=settings.gemini_api_key,
        )

        self.model_name = "gemini-2.5-flash"

        self.model = genai.GenerativeModel(
            self.model_name,
        )

        self.llm_logger = LLMLogger()
    @property
    def provider_name(
        self,
    ) -> str:
        return "gemini"

    def generate(
        self,
        prompt: str,
        prompt_name: str | None = None,
        prompt_version: str | None = None,
    ) -> str:
        start_time = now()
        last_exception: Exception | None = None

        for attempt in range(settings.llm_max_retries + 1):
            try:
                response = self.model.generate_content(
                    prompt,
                    request_options={
                        "timeout": settings.llm_timeout_seconds,
                    },
                )

                response_text = response.text

                latency_ms = (
                    now()
                    - start_time
                ) * 1000

                self.llm_logger.log(
                    LLMCallLog(
                        provider="gemini",
                        model=self.model_name,
                        prompt_name=prompt_name,
                        prompt_version=prompt_version,
                        prompt_length=len(prompt),
                        response_length=len(response_text),
                        success=True,
                        latency_ms=latency_ms,
                    )
                )

                return response_text

            except Exception as exc:
                last_exception = exc

                if attempt < settings.llm_max_retries:
                    time.sleep(
                        0.5 * (attempt + 1)
                    )
                    continue

        latency_ms = (
            now()
            - start_time
        ) * 1000

        self.llm_logger.log(
            LLMCallLog(
                provider="gemini",
                model=self.model_name,
                prompt_name=prompt_name,
                prompt_version=prompt_version,
                prompt_length=len(prompt),
                response_length=0,
                success=False,
                latency_ms=latency_ms,
                error_message=str(last_exception),
            )
        )

        raise last_exception