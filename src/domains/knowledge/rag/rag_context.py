from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RAGContextItem:
    source_number: int

    chunk_id: int
    document_id: int
    document_title: str

    content: str
    similarity_score: float
    chunk_index: int

    source_type: str
    source_uri: str | None

    category: str | None
    language: str


@dataclass(frozen=True, slots=True)
class RAGContext:
    text: str
    items: tuple[RAGContextItem, ...]
    source_count: int
    character_count: int