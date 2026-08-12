from datetime import datetime

from pydantic import BaseModel, Field
from src.domains.embeddings.schemas.embedding_generation_schema import (
    EmbeddingGenerationStatus,
)

class SingleJobIngestionResult(BaseModel):
    was_created: bool
    embedding_status: EmbeddingGenerationStatus
    
class JobIngestionResult(BaseModel):
    source: str
    fetched_count: int
    created_count: int
    updated_count: int
    failed_count: int

    embedding_created_count: int = 0
    embedding_updated_count: int = 0
    embedding_skipped_count: int = 0

    errors: list[str]


class JobIngestionTaskResponse(BaseModel):
    run_id: int
    task_id: str
    status: str
    source: str


class JobIngestionRunResponse(BaseModel):
    id: int
    task_id: str
    source: str
    status: str

    fetched_count: int
    created_count: int
    updated_count: int
    failed_count: int

    embedding_created_count: int
    embedding_updated_count: int
    embedding_skipped_count: int

    errors: list[str]

    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class JobSourceIngestionRequest(BaseModel):
    source: str = Field(
        pattern="^(fake|adzuna)$",
    )

    query: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    location: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )