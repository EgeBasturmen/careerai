from sqlalchemy.orm import Session

from src.domains.embeddings.clients.factory import (
    get_embedding_client,
)
from src.domains.embeddings.services.embedding_service import (
    EmbeddingService,
)
from src.domains.knowledge.cache.base_knowledge_version_provider import (
    KnowledgeVersionProvider,
)
from src.domains.knowledge.cache.knowledge_version_provider_factory import (
    get_knowledge_version_provider,
)
from src.domains.knowledge.chunking.recursive_text_chunker import (
    RecursiveTextChunker,
)
from src.domains.knowledge.models.knowledge_document import (
    KnowledgeDocument,
)
from src.domains.knowledge.repositories.knowledge_chunk_repository import (
    KnowledgeChunkRepository,
)
from src.domains.knowledge.repositories.knowledge_document_repository import (
    KnowledgeDocumentRepository,
)


class KnowledgeIngestionService:
    def __init__(
        self,
        db: Session,
        version_provider: (
            KnowledgeVersionProvider | None
        ) = None,
    ):
        self.document_repository = (
            KnowledgeDocumentRepository(db)
        )

        self.chunk_repository = (
            KnowledgeChunkRepository(db)
        )

        self.chunker = RecursiveTextChunker(
            chunk_size=1000,
            chunk_overlap=150,
        )

        self.embedding_client = (
            get_embedding_client()
        )

        self.embedding_service = EmbeddingService(
            client=self.embedding_client,
        )

        self.version_provider = (
            version_provider
            or get_knowledge_version_provider()
        )

    def ingest(
        self,
        document: KnowledgeDocument,
    ) -> KnowledgeDocument:
        self.document_repository.mark_processing(
            document,
        )

        text_chunks = self.chunker.split(
            document.content,
        )

        if not text_chunks:
            raise ValueError(
                "Document content produced no chunks"
            )

        chunk_texts = [
            chunk.content
            for chunk in text_chunks
        ]

        embedding_result = (
            self.embedding_service.embed_texts(
                chunk_texts,
            )
        )

        if (
            len(embedding_result.vectors)
            != len(text_chunks)
        ):
            raise ValueError(
                "Embedding count does not match "
                "chunk count"
            )

        self.chunk_repository.delete_by_document_id(
            document.id,
        )

        chunk_models = []

        for text_chunk, vector in zip(
            text_chunks,
            embedding_result.vectors,
            strict=True,
        ):
            chunk_model = (
                self.chunk_repository.create(
                    document_id=document.id,
                    chunk_index=text_chunk.index,
                    content=text_chunk.content,
                    character_count=(
                        text_chunk.character_count
                    ),
                    embedding_provider=(
                        embedding_result.provider
                    ),
                    embedding_model_name=(
                        embedding_result.model
                    ),
                    embedding_dimension=(
                        embedding_result.dimension
                    ),
                    embedding=vector,
                    chunk_metadata={
                        "start_character": (
                            text_chunk.start_character
                        ),
                        "end_character": (
                            text_chunk.end_character
                        ),
                        "category": (
                            document.category
                        ),
                        "language": (
                            document.language
                        ),
                    },
                )
            )

            chunk_models.append(
                chunk_model
            )

        self.chunk_repository.create_many(
            chunk_models,
        )

        completed_document = (
            self.document_repository
            .mark_completed(
                document=document,
                chunk_count=len(
                    chunk_models
                ),
            )
        )

        self.version_provider.increment_version()

        return completed_document