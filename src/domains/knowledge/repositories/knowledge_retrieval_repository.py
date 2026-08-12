from sqlalchemy.orm import Session

from src.domains.knowledge.models.knowledge_chunk import (
    KnowledgeChunk,
)
from src.domains.knowledge.models.knowledge_document import (
    KnowledgeDocument,
)
from sqlalchemy.orm import Session

from src.domains.knowledge.models.knowledge_chunk import (
    KnowledgeChunk,
)
from src.domains.knowledge.models.knowledge_document import (
    KnowledgeDocument,
)
from src.domains.knowledge.schemas.knowledge_retrieval_schema import (
    KnowledgeRetrievalCandidate,
)

class KnowledgeRetrievalRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def search(
        self,
        query_vector: list[float],
        embedding_model_name: str,
        limit: int = 5,
        minimum_similarity: float = 0.20,
        category: str | None = None,
        language: str | None = None,
    ) -> list[
        tuple[
            KnowledgeChunk,
            KnowledgeDocument,
            float,
        ]
    ]:
        distance_expression = (
            KnowledgeChunk.embedding
            .cosine_distance(
                query_vector,
            )
        )

        query = (
            self.db.query(
                KnowledgeChunk,
                KnowledgeDocument,
                distance_expression.label(
                    "distance",
                ),
            )
            .join(
                KnowledgeDocument,
                KnowledgeDocument.id
                == KnowledgeChunk.document_id,
            )
            .filter(
                KnowledgeChunk.embedding_model_name
                == embedding_model_name,
                KnowledgeDocument.ingestion_status
                == "COMPLETED",
            )
        )

        if category:
            query = query.filter(
                KnowledgeDocument.category
                == category,
            )

        if language:
            query = query.filter(
                KnowledgeDocument.language
                == language,
            )

        maximum_distance = (
            1.0 - minimum_similarity
        )

        query = query.filter(
            distance_expression
            <= maximum_distance,
        )

        rows = (
            query
            .order_by(
                distance_expression.asc(),
                KnowledgeChunk.id.asc(),
            )
            .limit(limit)
            .all()
        )

        results: list[
            tuple[
                KnowledgeChunk,
                KnowledgeDocument,
                float,
            ]
        ] = []

        for chunk, document, distance in rows:
            if distance is None:
                continue

            similarity = (
                1.0 - float(distance)
            )

            results.append(
                (
                    chunk,
                    document,
                    similarity,
                )
            )

        return results
    
    def list_candidates(
        self,
        *,
        category: str | None = None,
        language: str | None = None,
        candidate_limit: int = 1000,
    ) -> list[KnowledgeRetrievalCandidate]:
        query = (
            self.db.query(
                KnowledgeChunk,
                KnowledgeDocument,
            )
            .join(
                KnowledgeDocument,
                KnowledgeDocument.id
                == KnowledgeChunk.document_id,
            )
            .filter(
                KnowledgeDocument.ingestion_status
                == "COMPLETED",

            )
        )

        if category is not None:
            query = query.filter(
                KnowledgeDocument.category
                == category
            )

        if language is not None:
            query = query.filter(
                KnowledgeDocument.language
                == language
            )

        rows = (
            query
            .order_by(
                KnowledgeDocument.id.asc(),
                KnowledgeChunk.chunk_index.asc(),
            )
            .limit(candidate_limit)
            .all()
        )

        return [
            KnowledgeRetrievalCandidate(
                chunk_id=chunk.id,
                document_id=document.id,
                chunk_index=chunk.chunk_index,
                document_title=document.title,
                category=document.category,
                language=document.language,
                content=chunk.content,
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
            for chunk, document in rows
        ]