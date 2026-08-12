from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.domains.knowledge.repositories.knowledge_chunk_repository import (
    KnowledgeChunkRepository,
)
from src.domains.knowledge.repositories.knowledge_document_repository import (
    KnowledgeDocumentRepository,
)
from src.domains.knowledge.schemas.knowledge_schema import (
    KnowledgeChunkResponse,
    KnowledgeDocumentCreateRequest,
    KnowledgeDocumentDetailResponse,
    KnowledgeDocumentResponse,
)
from src.domains.knowledge.services.knowledge_ingestion_service import (
    KnowledgeIngestionService,
)
from src.domains.knowledge.cache.base_knowledge_version_provider import (
    KnowledgeVersionProvider,
)
from src.domains.knowledge.cache.knowledge_version_provider_factory import (
    get_knowledge_version_provider,
)

class KnowledgeService:
    def __init__(
        self,
        db: Session,
        version_provider: (
            KnowledgeVersionProvider | None
        ) = None,
    ):
        self.db = db

        self.version_provider = (
            version_provider
            or get_knowledge_version_provider()
        )

        self.document_repository = (
            KnowledgeDocumentRepository(db)
        )

        self.chunk_repository = (
            KnowledgeChunkRepository(db)
        )

        self.ingestion_service = (
            KnowledgeIngestionService(
                db=db,
                version_provider=(
                    self.version_provider
                ),
            )
        )

    def create_and_ingest(
        self,
        request: KnowledgeDocumentCreateRequest,
    ) -> KnowledgeDocumentResponse:
        document = (
            self.document_repository.create(
                title=request.title,
                source_type=request.source_type,
                source_uri=request.source_uri,
                category=request.category,
                language=request.language,
                content=request.content,
                document_metadata=(
                    request.document_metadata
                ),
            )
        )

        try:
            self.db.commit()
            self.db.refresh(document)

        except Exception:
            self.db.rollback()
            raise

        try:
            ingested_document = (
                self.ingestion_service.ingest(
                    document,
                )
            )

            self.db.commit()
            self.db.refresh(
                ingested_document
            )

        except Exception as exc:
            document_id = document.id

            self.db.rollback()

            persisted_document = (
                self.document_repository
                .get_by_id(
                    document_id,
                )
            )

            if persisted_document is not None:
                try:
                    self.document_repository.mark_failed(
                        document=persisted_document,
                        error_message=(
                            f"{type(exc).__name__}: {exc}"
                        ),
                    )

                    self.db.commit()

                except Exception:
                    self.db.rollback()
                    raise

            raise

        self.version_provider.increment_version()

        return (
            KnowledgeDocumentResponse
            .model_validate(
                ingested_document
            )
        )

    def get_document(
        self,
        document_id: int,
    ) -> KnowledgeDocumentDetailResponse:
        document = (
            self.document_repository.get_by_id(
                document_id,
            )
        )

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Knowledge document not found"
                ),
            )

        chunks = (
            self.chunk_repository
            .list_by_document_id(
                document_id=document.id,
            )
        )

        document_response = (
            KnowledgeDocumentResponse
            .model_validate(
                document
            )
        )

        return KnowledgeDocumentDetailResponse(
            **document_response.model_dump(),
            chunks=[
                KnowledgeChunkResponse
                .model_validate(chunk)
                for chunk in chunks
            ],
        )

    def list_documents(
        self,
        category: str | None = None,
        language: str | None = None,
        ingestion_status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[KnowledgeDocumentResponse]:
        documents = (
            self.document_repository.list_all(
                category=category,
                language=language,
                ingestion_status=(
                    ingestion_status
                ),
                limit=limit,
                offset=offset,
            )
        )

        return [
            KnowledgeDocumentResponse
            .model_validate(document)
            for document in documents
        ]
    
    def delete_document(
        self,
        document_id: int,
    ) -> None:
        document = (
            self.document_repository
            .get_by_id(
                document_id,
            )
        )

        if document is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Knowledge document not found"
                ),
            )

        try:
            self.chunk_repository.delete_by_document_id(
                document.id,
            )

            self.document_repository.delete(
                document,
            )

            self.db.commit()

        except Exception:
            self.db.rollback()
            raise

        self.version_provider.increment_version()