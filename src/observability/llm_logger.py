import time
from dataclasses import dataclass

from src.core.logging.logger import logger


@dataclass
class LLMCallLog:
    provider: str
    model: str
    prompt_length: int
    response_length: int
    success: bool
    latency_ms: float
    prompt_name: str | None = None
    prompt_version: str | None = None
    error_message: str | None = None


class LLMLogger:
    def log(
        self,
        call_log: LLMCallLog,
    ) -> None:
        logger.info(
            {
                "event": "llm_call",
                "provider": call_log.provider,
                "model": call_log.model,
                "prompt_name": call_log.prompt_name,
                "prompt_version": call_log.prompt_version,
                "prompt_length": call_log.prompt_length,
                "response_length": call_log.response_length,
                "success": call_log.success,
                "latency_ms": round(call_log.latency_ms, 2),
                "error_message": call_log.error_message,
            }
        )


def now() -> float:
    return time.perf_counter()