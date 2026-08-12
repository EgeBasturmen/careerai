from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class RAGRunChunkResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    knowledge_chunk_id: int | None
    knowledge_document_id: int | None

    source_number: int
    retrieval_rank: int
    chunk_index: int

    document_title: str
    chunk_content: str

    similarity_score: float

    was_included_in_context: bool
    was_cited: bool

    chunk_metadata: dict[str, Any]

    created_at: datetime


class RAGRunListItemResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    question: str

    category: str | None
    language: str | None

    generation_status: str
    sufficient_context: bool | None
    confidence: float | None

    retrieval_result_count: int
    context_source_count: int
    context_character_count: int

    embedding_provider: str | None
    embedding_model_name: str | None

    llm_provider: str | None
    llm_model_name: str | None

    prompt_name: str
    prompt_version: str

    retrieval_latency_ms: float | None
    context_build_latency_ms: float | None
    prompt_build_latency_ms: float | None
    llm_latency_ms: float | None
    total_latency_ms: float | None

    created_at: datetime
    completed_at: datetime | None


class RAGRunListResponse(BaseModel):
    items: list[
        RAGRunListItemResponse
    ]

    total: int
    limit: int
    offset: int


class RAGRunDetailResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    user_id: int

    question: str
    answer: str | None

    category: str | None
    language: str | None

    generation_status: str
    sufficient_context: bool | None
    confidence: float | None

    retrieval_limit: int
    minimum_similarity: float

    retrieval_result_count: int
    context_source_count: int
    context_character_count: int

    embedding_provider: str | None
    embedding_model_name: str | None

    llm_provider: str | None
    llm_model_name: str | None

    prompt_name: str
    prompt_version: str

    retrieval_latency_ms: float | None
    context_build_latency_ms: float | None
    prompt_build_latency_ms: float | None
    llm_latency_ms: float | None
    total_latency_ms: float | None

    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None

    citations: list[
        dict[str, Any]
    ]

    validation_errors: list[str]

    error_type: str | None
    error_message: str | None

    created_at: datetime
    completed_at: datetime | None

    chunks: list[
        RAGRunChunkResponse
    ] = Field(
        default_factory=list,
    )