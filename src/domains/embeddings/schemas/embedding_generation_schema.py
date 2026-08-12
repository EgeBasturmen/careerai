from enum import StrEnum

from pydantic import BaseModel


class EmbeddingGenerationStatus(
    StrEnum,
):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    SKIPPED = "SKIPPED"


class EmbeddingGenerationResult(
    BaseModel,
):
    status: EmbeddingGenerationStatus
    entity_type: str
    entity_id: int
    model_name: str
    reason: str | None = None