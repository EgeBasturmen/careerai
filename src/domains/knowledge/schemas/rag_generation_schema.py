from pydantic import (
    BaseModel,
    Field,
)


class RAGGeneratedCitationSchema(
    BaseModel
):
    source_number: int = Field(
        ge=1,
    )

    claim: str = Field(
        min_length=1,
        max_length=2000,
    )


class RAGGeneratedAnswerSchema(
    BaseModel
):
    answer: str = Field(
        min_length=1,
    )

    citations: list[
        RAGGeneratedCitationSchema
    ] = Field(
        default_factory=list,
    )

    sufficient_context: bool

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )