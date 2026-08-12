from pydantic import (
    BaseModel,
    Field,
)


class QueryRewriteRequest(BaseModel):
    query: str = Field(
        min_length=2,
        max_length=4000,
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


class QueryRewriteResponse(BaseModel):
    original_query: str
    rewritten_query: str

    was_rewritten: bool

    rewrite_provider: str | None = None
    rewrite_model_name: str | None = None

    rewrite_latency_ms: float = 0.0

    fallback_used: bool = False
    fallback_reason: str | None = None