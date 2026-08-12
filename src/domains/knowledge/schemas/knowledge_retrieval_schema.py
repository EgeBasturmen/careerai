from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field


@dataclass(
    frozen=True,
    slots=True,
)
class KnowledgeRetrievalCandidate:
    chunk_id: int
    document_id: int
    chunk_index: int

    document_title: str
    category: str | None
    language: str

    content: str

    source_type: str
    source_uri: str | None

    document_metadata: dict[str, Any]
    chunk_metadata: dict[str, Any]


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(
        min_length=2,
        max_length=2000,
    )

    limit: int = Field(
        default=5,
        ge=1,
        le=50,
    )

    minimum_similarity: float = Field(
        default=0.20,
        ge=-1.0,
        le=1.0,
    )

    category: str | None = Field(
        default=None,
        max_length=100,
    )

    language: str | None = Field(
        default=None,
        min_length=2,
        max_length=10,
    )


class KnowledgeRetrievalResult(BaseModel):
    chunk_id: int
    document_id: int
    chunk_index: int

    document_title: str
    category: str | None
    language: str

    content: str

    similarity_score: float

    source_type: str
    source_uri: str | None

    document_metadata: dict[str, Any]
    chunk_metadata: dict[str, Any]


class KnowledgeSearchResponse(BaseModel):
    query: str

    embedding_provider: str
    embedding_model_name: str

    retriever_name: str

    reranker_name: str | None = None
    reranker_model_name: str | None = None

    candidate_result_count: int
    result_count: int

    minimum_similarity: float
    category: str | None
    language: str | None

    results: list[
        KnowledgeRetrievalResult
    ]