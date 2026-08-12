from unittest.mock import Mock

from src.domains.knowledge.models.knowledge_chunk import (
    KnowledgeChunk,
)
from src.domains.knowledge.repositories.knowledge_chunk_repository import (
    KnowledgeChunkRepository,
)


def test_create_adds_chunk_without_committing(
) -> None:
    db = Mock()

    repository = KnowledgeChunkRepository(
        db,
    )

    chunk = repository.create(
        document_id=1,
        chunk_index=0,
        content="FastAPI content",
        character_count=15,
        embedding_provider="fake",
        embedding_model_name="fake-model",
        embedding_dimension=3,
        embedding=[0.1, 0.2, 0.3],
    )

    assert isinstance(
        chunk,
        KnowledgeChunk,
    )

    db.add.assert_called_once_with(
        chunk
    )

    db.commit.assert_not_called()


def test_create_many_adds_flushes_and_refreshes_chunks(
) -> None:
    db = Mock()

    repository = KnowledgeChunkRepository(
        db,
    )

    first_chunk = Mock()
    second_chunk = Mock()

    result = repository.create_many(
        [
            first_chunk,
            second_chunk,
        ]
    )

    assert result == [
        first_chunk,
        second_chunk,
    ]

    db.add_all.assert_called_once_with(
        [
            first_chunk,
            second_chunk,
        ]
    )

    db.flush.assert_called_once_with()

    assert db.refresh.call_count == 2

    db.refresh.assert_any_call(
        first_chunk
    )

    db.refresh.assert_any_call(
        second_chunk
    )

    db.commit.assert_not_called()


def test_create_many_returns_empty_list_without_database_calls(
) -> None:
    db = Mock()

    repository = KnowledgeChunkRepository(
        db,
    )

    result = repository.create_many(
        []
    )

    assert result == []

    db.add_all.assert_not_called()
    db.flush.assert_not_called()
    db.refresh.assert_not_called()
    db.commit.assert_not_called()


def test_delete_by_document_id_flushes_without_committing(
) -> None:
    db = Mock()

    query = Mock()
    filtered_query = Mock()

    db.query.return_value = query
    query.filter.return_value = (
        filtered_query
    )

    filtered_query.delete.return_value = 4

    repository = KnowledgeChunkRepository(
        db,
    )

    result = (
        repository
        .delete_by_document_id(
            document_id=12,
        )
    )

    assert result == 4

    filtered_query.delete.assert_called_once_with(
        synchronize_session=False,
    )

    db.flush.assert_called_once_with()
    db.commit.assert_not_called()