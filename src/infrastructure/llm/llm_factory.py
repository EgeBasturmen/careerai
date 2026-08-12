from src.core.config.settings import settings
from src.infrastructure.llm.fake_llm_client import FakeLLMClient
from src.infrastructure.llm.gemini_llm_client import GeminiLLMClient
from src.infrastructure.llm.base import LLMClient


def get_llm_client() -> LLMClient:
    if settings.llm_provider == "gemini":
        return GeminiLLMClient()

    return FakeLLMClient()