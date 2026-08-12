from unittest.mock import Mock

from src.domains.knowledge.repositories.knowledge_document_repository import (
    KnowledgeDocumentRepository,
)


def test_create_adds_flushes_and_refreshes_document_without_committing(
) -> None:
    db = Mock()

    repository = KnowledgeDocumentRepository(
        db=db,
    )

    document = repository.create(
        title="FastAPI Guide",
        source_type="manual",
        content="FastAPI knowledge content",
        source_uri=None,
        category="backend",
        language="en",
        document_metadata={
            "author": "Test Author",
        },
    )

    db.add.assert_called_once_with(
        document,
    )

    db.flush.assert_called_once_with()

    db.refresh.assert_called_once_with(
        document,
    )

    db.commit.assert_not_called()

    assert document.title == "FastAPI Guide"
    assert document.source_type == "manual"
    assert document.content == (
        "FastAPI knowledge content"
    )
    assert document.source_uri is None
    assert document.category == "backend"
    assert document.language == "en"
    assert document.document_metadata == {
        "author": "Test Author",
    }
    assert document.ingestion_status == "PENDING"
    assert document.chunk_count == 0


def test_mark_processing_updates_status_without_committing(
) -> None:
    db = Mock()

    repository = KnowledgeDocumentRepository(
        db=db,
    )

    document = Mock(
        ingestion_status=None,
        chunk_count=0,
        error_message=None,
    )

    result = repository.mark_processing(
        document=document,
    )

    assert result is document
    assert document.ingestion_status == "PROCESSING"
    assert document.error_message is None

    db.flush.assert_called_once_with()
    db.refresh.assert_called_once_with(
        document,
    )
    db.commit.assert_not_called()


def test_mark_completed_updates_status_and_chunk_count_without_committing(
) -> None:
    db = Mock()

    repository = KnowledgeDocumentRepository(
        db=db,
    )

    document = Mock(
        ingestion_status=None,
        chunk_count=0,
        error_message=None,
    )

    result = repository.mark_completed(
        document=document,
        chunk_count=5,
    )

    assert result is document
    assert document.ingestion_status == "COMPLETED"
    assert document.chunk_count == 5
    assert document.error_message is None

    db.flush.assert_called_once_with()
    db.refresh.assert_called_once_with(
        document,
    )
    db.commit.assert_not_called()


def test_mark_failed_updates_status_and_error_without_committing(
) -> None:
    db = Mock()

    repository = KnowledgeDocumentRepository(
        db=db,
    )

    document = Mock(
        ingestion_status=None,
        chunk_count=0,
        error_message=None,
    )

    result = repository.mark_failed(
        document=document,
        error_message=(
            "RuntimeError: Embedding failed"
        ),
    )

    assert result is document
    assert document.ingestion_status == "FAILED"
    assert document.error_message == (
        "RuntimeError: Embedding failed"
    )

    db.flush.assert_called_once_with()
    db.refresh.assert_called_once_with(
        document,
    )
    db.commit.assert_not_called()


def test_delete_deletes_and_flushes_without_committing(
) -> None:
    db = Mock()

    repository = KnowledgeDocumentRepository(
        db=db,
    )

    document = Mock(
        ingestion_status=None,
        chunk_count=0,
        error_message=None,
    )

    repository.delete(
        document=document,
    )

    db.delete.assert_called_once_with(
        document,
    )

    db.flush.assert_called_once_with()
    db.commit.assert_not_called()