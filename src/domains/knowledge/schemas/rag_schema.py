from pydantic import (
    BaseModel,
    Field,
)


class RAGQuestionRequest(BaseModel):
    question: str = Field(
        min_length=2,
        max_length=4000,
    )

    retrieval_limit: int = Field(
        default=5,
        ge=1,
        le=20,
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


class RAGSourceResponse(BaseModel):
    source_number: int

    chunk_id: int
    document_id: int
    document_title: str

    similarity_score: float

    source_type: str
    source_uri: str | None

    category: str | None
    language: str


class RAGCitationResponse(BaseModel):
    source_number: int
    claim: str


class RAGAnswerResponse(BaseModel):
    question: str
    answer: str

    sufficient_context: bool
    confidence: float

    generation_status: str

    candidate_result_count: int
    retrieval_result_count: int
    original_query: str
    rewritten_query: str
    was_rewritten: bool

    rewrite_provider: str | None = None
    rewrite_model_name: str | None = None

    rewrite_latency_ms: float = 0.0

    rewrite_fallback_used: bool = False
    rewrite_fallback_reason: str | None = None

    retriever_name: str
    reranker_name: str | None = None
    reranker_model_name: str | None = None

    context_source_count: int
    context_character_count: int

    embedding_provider: str
    embedding_model_name: str

    citations: list[
        RAGCitationResponse
    ]

    sources: list[
        RAGSourceResponse
    ]

    validation_errors: list[str]