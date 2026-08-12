from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from src.domains.knowledge.services.knowledge_service import (
    KnowledgeService,
)


def test_create_and_ingest_commits_and_increments_version(
) -> None:
    db = Mock()
    version_provider = Mock()

    service = KnowledgeService(
        db=db,
        version_provider=version_provider,
    )

    service.document_repository = Mock()
    service.ingestion_service = Mock()

    request = Mock()
    request.title = "FastAPI Guide"
    request.source_type = "manual"
    request.source_uri = None
    request.category = "backend"
    request.language = "en"
    request.content = "FastAPI knowledge content"
    request.document_metadata = {
        "author": "Test Author",
    }

    document = Mock()
    document.id = 12

    ingested_document = Mock()
    response = Mock()

    (
        service.document_repository
        .create
        .return_value
    ) = document

    (
        service.ingestion_service
        .ingest
        .return_value
    ) = ingested_document

    with patch(
        "src.domains.knowledge.services."
        "knowledge_service."
        "KnowledgeDocumentResponse."
        "model_validate",
        return_value=response,
    ) as model_validate:
        result = service.create_and_ingest(
            request=request,
        )

    assert result is response

    (
        service.document_repository
        .create
        .assert_called_once_with(
            title="FastAPI Guide",
            source_type="manual",
            source_uri=None,
            category="backend",
            language="en",
            content=(
                "FastAPI knowledge content"
            ),
            document_metadata={
                "author": "Test Author",
            },
        )
    )

    (
        service.ingestion_service
        .ingest
        .assert_called_once_with(
            document,
        )
    )

    assert db.commit.call_count == 2

    db.refresh.assert_any_call(
        document,
    )

    db.refresh.assert_any_call(
        ingested_document,
    )

    assert db.refresh.call_count == 2

    db.rollback.assert_not_called()

    (
        version_provider
        .increment_version
        .assert_called_once_with()
    )

    model_validate.assert_called_once_with(
        ingested_document,
    )


def test_create_and_ingest_marks_document_failed_when_ingestion_fails(
) -> None:
    db = Mock()
    version_provider = Mock()

    service = KnowledgeService(
        db=db,
        version_provider=version_provider,
    )

    service.document_repository = Mock()
    service.ingestion_service = Mock()

    request = Mock()
    request.title = "Broken Document"
    request.source_type = "manual"
    request.source_uri = None
    request.category = "backend"
    request.language = "en"
    request.content = "Broken content"
    request.document_metadata = {}

    document = Mock()
    document.id = 12

    persisted_document = Mock()
    persisted_document.id = 12

    (
        service.document_repository
        .create
        .return_value
    ) = document

    (
        service.document_repository
        .get_by_id
        .return_value
    ) = persisted_document

    (
        service.ingestion_service
        .ingest
        .side_effect
    ) = RuntimeError(
        "Embedding generation failed"
    )

    with pytest.raises(
        RuntimeError,
        match="Embedding generation failed",
    ):
        service.create_and_ingest(
            request=request,
        )

    (
        service.document_repository
        .create
        .assert_called_once_with(
            title="Broken Document",
            source_type="manual",
            source_uri=None,
            category="backend",
            language="en",
            content="Broken content",
            document_metadata={},
        )
    )

    (
        service.ingestion_service
        .ingest
        .assert_called_once_with(
            document,
        )
    )

    db.rollback.assert_called_once_with()

    (
        service.document_repository.get_by_id.assert_called_once_with(
            12,
        )
    )

    (
        service.document_repository
        .mark_failed
        .assert_called_once_with(
            document=persisted_document,
            error_message=(
                "RuntimeError: "
                "Embedding generation failed"
            ),
        )
    )

    assert db.commit.call_count == 2

    (
        version_provider
        .increment_version
        .assert_not_called()
    )


def test_delete_document_deletes_chunks_and_document_and_increments_version(
) -> None:
    db = Mock()
    version_provider = Mock()

    service = KnowledgeService(
        db=db,
        version_provider=version_provider,
    )

    document = Mock()
    document.id = 12

    service.document_repository = Mock()
    service.chunk_repository = Mock()

    (
        service.document_repository
        .get_by_id
        .return_value
    ) = document

    service.delete_document(
        document_id=12,
    )

    (
        service.document_repository.get_by_id.assert_called_once_with(
            12,
        )
    )

    (
        service.chunk_repository.delete_by_document_id.assert_called_once_with(
            12,
        )
    )

    (
        service.document_repository
        .delete
        .assert_called_once_with(
            document,
        )
    )

    db.commit.assert_called_once_with()
    db.rollback.assert_not_called()

    (
        version_provider
        .increment_version
        .assert_called_once_with()
    )


def test_delete_document_raises_not_found_when_document_does_not_exist(
) -> None:
    db = Mock()
    version_provider = Mock()

    service = KnowledgeService(
        db=db,
        version_provider=version_provider,
    )

    service.document_repository = Mock()
    service.chunk_repository = Mock()

    (
        service.document_repository
        .get_by_id
        .return_value
    ) = None

    with pytest.raises(
        HTTPException,
    ) as exc_info:
        service.delete_document(
            document_id=999,
        )

    assert (
        exc_info.value.status_code
        == 404
    )

    assert (
        exc_info.value.detail
        == "Knowledge document not found"
    )

    (
        service.chunk_repository
        .delete_by_document_id
        .assert_not_called()
    )

    (
        service.document_repository
        .delete
        .assert_not_called()
    )

    db.commit.assert_not_called()
    db.rollback.assert_not_called()

    (
        version_provider
        .increment_version
        .assert_not_called()
    )


def test_delete_document_rolls_back_and_does_not_increment_version_when_delete_fails(
) -> None:
    db = Mock()
    version_provider = Mock()

    service = KnowledgeService(
        db=db,
        version_provider=version_provider,
    )

    document = Mock()
    document.id = 12

    service.document_repository = Mock()
    service.chunk_repository = Mock()

    (
        service.document_repository
        .get_by_id
        .return_value
    ) = document

    (
        service.document_repository
        .delete
        .side_effect
    ) = RuntimeError(
        "Database delete failed"
    )

    with pytest.raises(
        RuntimeError,
        match="Database delete failed",
    ):
        service.delete_document(
            document_id=12,
        )

    (
        service.chunk_repository.delete_by_document_id.assert_called_once_with(
            12,
        )
    )

    (
        service.document_repository
        .delete
        .assert_called_once_with(
            document,
        )
    )

    db.rollback.assert_called_once_with()
    db.commit.assert_not_called()

    (
        version_provider
        .increment_version
        .assert_not_called()
    )