from unittest.mock import Mock
import pytest
from src.domains.knowledge.services.knowledge_ingestion_service import (
    KnowledgeIngestionService,
)


def test_ingest_increments_knowledge_version_after_completion(
) -> None:
    db = Mock()
    version_provider = Mock()

    service = KnowledgeIngestionService(
        db=db,
        version_provider=version_provider,
    )

    document = Mock()
    document.id = 1
    document.content = (
        "Python backend development "
        "with FastAPI and PostgreSQL."
    )
    document.category = "backend"
    document.language = "en"

    text_chunk = Mock()
    text_chunk.index = 0
    text_chunk.content = document.content
    text_chunk.character_count = len(
        document.content
    )
    text_chunk.start_character = 0
    text_chunk.end_character = len(
        document.content
    )

    service.chunker = Mock()
    service.chunker.split.return_value = [
        text_chunk
    ]

    embedding_result = Mock()
    embedding_result.vectors = [
        [0.1, 0.2, 0.3]
    ]
    embedding_result.provider = "fake"
    embedding_result.model = "fake-model"
    embedding_result.dimension = 3

    service.embedding_service = Mock()
    (
        service.embedding_service
        .embed_texts
        .return_value
    ) = embedding_result

    chunk_model = Mock()

    service.chunk_repository = Mock()
    (
        service.chunk_repository
        .create
        .return_value
    ) = chunk_model

    completed_document = Mock()

    service.document_repository = Mock()
    (
        service.document_repository
        .mark_completed
        .return_value
    ) = completed_document

    result = service.ingest(
        document=document,
    )

    assert result is completed_document

    version_provider.increment_version.assert_called_once_with()

    (
        service.document_repository
        .mark_completed
        .assert_called_once_with(
            document=document,
            chunk_count=1,
        )
    )

def test_ingest_does_not_increment_version_when_ingestion_fails(
) -> None:
    db = Mock()
    version_provider = Mock()

    service = KnowledgeIngestionService(
        db=db,
        version_provider=version_provider,
    )

    document = Mock()
    document.content = ""
    document.id = 1

    service.chunker = Mock()
    service.chunker.split.return_value = []

    service.document_repository = Mock()

    with pytest.raises(
        ValueError,
        match=(
            "Document content produced no chunks"
        ),
    ):
        service.ingest(
            document=document,
        )

    version_provider.increment_version.assert_not_called()

    db.rollback.assert_not_called()

    (
        service.document_repository
        .mark_failed
        .assert_not_called()
    )