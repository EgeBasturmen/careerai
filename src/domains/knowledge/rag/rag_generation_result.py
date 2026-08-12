from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RAGGeneratedCitation:
    source_number: int
    claim: str


@dataclass(frozen=True, slots=True)
class RAGGenerationResult:
    answer: str

    citations: tuple[
        RAGGeneratedCitation,
        ...
    ]

    sufficient_context: bool
    confidence: float

    raw_response: str