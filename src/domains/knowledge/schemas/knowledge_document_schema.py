from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class KnowledgeDocumentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    title: str
    source_type: str
    source_uri: str | None
    category: str | None
    language: str
    content: str
    document_metadata: dict[str, Any]
    ingestion_status: str
    chunk_count: int
    error_message: str | None
    created_at: datetime