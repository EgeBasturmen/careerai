from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class KnowledgeDocumentCreateRequest(
    BaseModel
):
    title: str = Field(
        min_length=1,
        max_length=255,
    )

    source_type: str = Field(
        default="manual",
        min_length=1,
        max_length=50,
    )

    source_uri: str | None = Field(
        default=None,
        max_length=1000,
    )

    category: str | None = Field(
        default=None,
        max_length=100,
    )

    language: str = Field(
        default="en",
        min_length=2,
        max_length=10,
    )

    content: str = Field(
        min_length=1,
    )

    document_metadata: dict[
        str,
        Any,
    ] = Field(
        default_factory=dict,
    )


class KnowledgeDocumentResponse(
    BaseModel
):
    id: int

    title: str
    source_type: str
    source_uri: str | None

    category: str | None
    language: str

    ingestion_status: str
    ingestion_error: str | None
    chunk_count: int

    document_metadata: dict

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class KnowledgeChunkResponse(
    BaseModel
):
    id: int
    document_id: int
    chunk_index: int

    content: str
    token_count: int | None
    character_count: int

    embedding_provider: str
    embedding_model_name: str
    embedding_dimension: int

    chunk_metadata: dict

    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class KnowledgeDocumentDetailResponse(
    KnowledgeDocumentResponse
):
    chunks: list[
        KnowledgeChunkResponse
    ]