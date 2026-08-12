from sqlalchemy.orm import Session

from src.domains.knowledge.models.knowledge_chunk import (
    KnowledgeChunk,
)


class KnowledgeChunkRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        document_id: int,
        chunk_index: int,
        content: str,
        character_count: int,
        embedding_provider: str,
        embedding_model_name: str,
        embedding_dimension: int,
        embedding: list[float],
        token_count: int | None = None,
        chunk_metadata: dict | None = None,
    ) -> KnowledgeChunk:
        chunk = KnowledgeChunk(
            document_id=document_id,
            chunk_index=chunk_index,
            content=content,
            character_count=character_count,
            token_count=token_count,
            embedding_provider=(
                embedding_provider
            ),
            embedding_model_name=(
                embedding_model_name
            ),
            embedding_dimension=(
                embedding_dimension
            ),
            embedding=embedding,
            chunk_metadata=(
                chunk_metadata or {}
            ),
        )

        self.db.add(chunk)

        return chunk

    def create_many(
        self,
        chunks: list[KnowledgeChunk],
    ) -> list[KnowledgeChunk]:
        if not chunks:
            return []

        self.db.add_all(chunks)
        self.db.flush()

        for chunk in chunks:
            self.db.refresh(chunk)

        return chunks

    def delete_by_document_id(
        self,
        document_id: int,
    ) -> int:
        deleted_count = (
            self.db.query(KnowledgeChunk)
            .filter(
                KnowledgeChunk.document_id
                == document_id,
            )
            .delete(
                synchronize_session=False,
            )
        )

        self.db.flush()

        return int(deleted_count)

    def list_by_document_id(
        self,
        document_id: int,
    ) -> list[KnowledgeChunk]:
        return (
            self.db.query(KnowledgeChunk)
            .filter(
                KnowledgeChunk.document_id
                == document_id,
            )
            .order_by(
                KnowledgeChunk.chunk_index.asc()
            )
            .all()
        )