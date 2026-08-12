from unittest.mock import Mock

import pytest

from src.domains.knowledge.cache.retrieval_cache_key_builder import (
    RetrievalCacheKeyBuilder,
)
from src.domains.knowledge.schemas.knowledge_retrieval_schema import (
    KnowledgeSearchRequest,
)


@pytest.fixture
def version_provider() -> Mock:
    provider = Mock()
    provider.get_version.return_value = 7

    return provider


@pytest.fixture
def search_request(
) -> KnowledgeSearchRequest:
    return KnowledgeSearchRequest(
        query="python developer",
        limit=5,
        minimum_similarity=0.3,
        category="backend",
        language="en",
    )


def test_same_request_and_version_produce_same_key(
    version_provider: Mock,
    search_request: KnowledgeSearchRequest,
) -> None:
    builder = RetrievalCacheKeyBuilder(
        version_provider=version_provider,
    )

    first_key = builder.build(
        search_request
    )

    second_key = builder.build(
        search_request
    )

    assert first_key == second_key

    assert first_key.startswith(
        "knowledge:retrieval:7:"
    )

    assert (
        version_provider
        .get_version
        .call_count
        == 2
    )


def test_version_change_produces_different_key(
    search_request: KnowledgeSearchRequest,
) -> None:
    version_provider = Mock()

    version_provider.get_version.side_effect = [
        7,
        8,
    ]

    builder = RetrievalCacheKeyBuilder(
        version_provider=version_provider,
    )

    first_key = builder.build(
        search_request
    )

    second_key = builder.build(
        search_request
    )

    assert first_key != second_key

    assert first_key.startswith(
        "knowledge:retrieval:7:"
    )

    assert second_key.startswith(
        "knowledge:retrieval:8:"
    )


def test_query_change_produces_different_key(
    version_provider: Mock,
    search_request: KnowledgeSearchRequest,
) -> None:
    builder = RetrievalCacheKeyBuilder(
        version_provider=version_provider,
    )

    changed_request = (
        search_request.model_copy(
            update={
                "query": "java developer",
            }
        )
    )

    original_key = builder.build(
        search_request
    )

    changed_key = builder.build(
        changed_request
    )

    assert original_key != changed_key


def test_limit_change_produces_different_key(
    version_provider: Mock,
    search_request: KnowledgeSearchRequest,
) -> None:
    builder = RetrievalCacheKeyBuilder(
        version_provider=version_provider,
    )

    changed_request = (
        search_request.model_copy(
            update={
                "limit": 10,
            }
        )
    )

    original_key = builder.build(
        search_request
    )

    changed_key = builder.build(
        changed_request
    )

    assert original_key != changed_key


def test_minimum_similarity_change_produces_different_key(
    version_provider: Mock,
    search_request: KnowledgeSearchRequest,
) -> None:
    builder = RetrievalCacheKeyBuilder(
        version_provider=version_provider,
    )

    changed_request = (
        search_request.model_copy(
            update={
                "minimum_similarity": 0.6,
            }
        )
    )

    original_key = builder.build(
        search_request
    )

    changed_key = builder.build(
        changed_request
    )

    assert original_key != changed_key


def test_category_change_produces_different_key(
    version_provider: Mock,
    search_request: KnowledgeSearchRequest,
) -> None:
    builder = RetrievalCacheKeyBuilder(
        version_provider=version_provider,
    )

    changed_request = (
        search_request.model_copy(
            update={
                "category": "machine-learning",
            }
        )
    )

    original_key = builder.build(
        search_request
    )

    changed_key = builder.build(
        changed_request
    )

    assert original_key != changed_key


def test_language_change_produces_different_key(
    version_provider: Mock,
    search_request: KnowledgeSearchRequest,
) -> None:
    builder = RetrievalCacheKeyBuilder(
        version_provider=version_provider,
    )

    changed_request = (
        search_request.model_copy(
            update={
                "language": "tr",
            }
        )
    )

    original_key = builder.build(
        search_request
    )

    changed_key = builder.build(
        changed_request
    )

    assert original_key != changed_key