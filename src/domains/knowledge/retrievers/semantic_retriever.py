from sqlalchemy.orm import Session

from src.domains.knowledge.repositories.knowledge_retrieval_repository import (
    KnowledgeRetrievalRepository,
)
from src.domains.knowledge.retrievers.base import (
    BaseKnowledgeRetriever,
)
from src.domains.knowledge.schemas.knowledge_retrieval_schema import (
    KnowledgeRetrievalResult,
)


class SemanticKnowledgeRetriever(
    BaseKnowledgeRetriever,
):
    def __init__(
        self,
        db: Session,
        embedding_model_name: str,
    ):
        self.repository = (
            KnowledgeRetrievalRepository(
                db
            )
        )

        self.embedding_model_name = (
            embedding_model_name
        )

    @property
    def retriever_name(
        self,
    ) -> str:
        return "semantic"

    def retrieve(
        self,
        *,
        query_text: str,
        query_embedding: list[float] | None,
        limit: int,
        minimum_similarity: float,
        category: str | None = None,
        language: str | None = None,
    ) -> list[KnowledgeRetrievalResult]:
        del query_text

        if query_embedding is None:
            raise ValueError(
                "Query embedding is required "
                "for semantic retrieval"
            )

        rows = self.repository.search(
            query_vector=query_embedding,
            embedding_model_name=(
                self.embedding_model_name
            ),
            limit=limit,
            minimum_similarity=(
                minimum_similarity
            ),
            category=category,
            language=language,
        )

        return [
            KnowledgeRetrievalResult(
                chunk_id=chunk.id,
                document_id=document.id,
                chunk_index=chunk.chunk_index,
                document_title=document.title,
                category=document.category,
                language=document.language,
                content=chunk.content,
                similarity_score=similarity,
                source_type=document.source_type,
                source_uri=document.source_uri,
                document_metadata=(
                    document.document_metadata
                    or {}
                ),
                chunk_metadata=(
                    chunk.chunk_metadata
                    or {}
                ),
            )
            for chunk, document, similarity in rows
        ]