from pydantic import BaseModel


class RAGErrorStatisticResponse(BaseModel):
    error_type: str
    count: int


class RAGStatisticsResponse(BaseModel):
    total_runs: int

    success_runs: int
    failed_runs: int
    no_context_runs: int
    invalid_generation_runs: int
    processing_runs: int

    success_rate: float
    failure_rate: float
    no_context_rate: float
    invalid_generation_rate: float

    cache_enabled_runs: int
    cache_hit_runs: int
    cache_miss_runs: int

    cache_hit_rate: float
    cache_miss_rate: float

    average_cache_read_latency_ms: float
    average_cache_write_latency_ms: float

    average_cache_hit_retrieval_latency_ms: float
    average_cache_miss_retrieval_latency_ms: float

    estimated_retrieval_latency_saved_ms: float

    average_retrieval_latency_ms: float
    average_context_build_latency_ms: float
    average_prompt_build_latency_ms: float
    average_llm_latency_ms: float
    average_total_latency_ms: float

    average_context_source_count: float
    citation_rate: float
    average_confidence: float | None

    top_errors: list[RAGErrorStatisticResponse]