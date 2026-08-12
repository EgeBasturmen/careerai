from pydantic import BaseModel, Field


class EmbeddingResult(BaseModel):
    provider: str
    model: str
    dimension: int = Field(
        ge=1,
    )
    vector: list[float]


class BatchEmbeddingResult(BaseModel):
    provider: str
    model: str
    dimension: int = Field(
        ge=1,
    )
    vectors: list[list[float]]