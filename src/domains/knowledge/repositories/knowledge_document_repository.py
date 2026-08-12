from sqlalchemy.orm import Session

from src.domains.knowledge.models.knowledge_document import (
    KnowledgeDocument,
)
from sqlalchemy import select

class KnowledgeDocumentRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        title: str,
        source_type: str,
        content: str,
        source_uri: str | None = None,
        category: str | None = None,
        language: str = "en",
        document_metadata: dict | None = None,
    ) -> KnowledgeDocument:
        document = KnowledgeDocument(
            title=title,
            source_type=source_type,
            source_uri=source_uri,
            category=category,
            language=language,
            content=content,
            document_metadata=(
                document_metadata or {}
            ),
            ingestion_status="PENDING",
            chunk_count=0,
        )

        self.db.add(document)
        self.db.flush()
        self.db.refresh(document)

        return document

    def get_by_id(
        self,
        document_id: int,
    ) -> KnowledgeDocument | None:
        return (
            self.db.query(KnowledgeDocument)
            .filter(
                KnowledgeDocument.id == document_id,
            )
            .first()
        )

    def list_all(
        self,
        category: str | None = None,
        language: str | None = None,
        ingestion_status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[KnowledgeDocument]:
        query = self.db.query(
            KnowledgeDocument
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

        if ingestion_status:
            query = query.filter(
                KnowledgeDocument.ingestion_status
                == ingestion_status,
            )

        return (
            query
            .order_by(
                KnowledgeDocument.id.desc()
            )
            .offset(offset)
            .limit(limit)
            .all()
        )

    def mark_processing(
        self,
        document: KnowledgeDocument,
    ) -> KnowledgeDocument:
        document.ingestion_status = "PROCESSING"
        document.ingestion_error = None

        self.db.flush()
        self.db.refresh(document)

        return document

    def mark_completed(
        self,
        document: KnowledgeDocument,
        chunk_count: int,
    ) -> KnowledgeDocument:
        document.ingestion_status = "COMPLETED"
        document.ingestion_error = None
        document.chunk_count = chunk_count

        self.db.flush()
        self.db.refresh(document)

        return document

    def mark_failed(
        self,
        document: KnowledgeDocument,
        error_message: str,
    ) -> KnowledgeDocument:
        document.ingestion_status = "FAILED"
        document.error_message = error_message
        document.ingestion_error = (
            error_message[:5000]
        )

        self.db.flush()
        self.db.refresh(document)

        return document

    def delete(
        self,
        document: KnowledgeDocument,
    ) -> None:
        self.db.delete(document)
        self.db.flush()


    def get_all(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[KnowledgeDocument]:
        statement = (
            select(KnowledgeDocument)
            .order_by(
                KnowledgeDocument.id.desc(),
            )
            .limit(limit)
            .offset(offset)
        )

        return list(
            self.db.scalars(statement).all()
        )