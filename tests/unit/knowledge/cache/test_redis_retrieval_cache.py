from unittest.mock import MagicMock

import pytest
from redis.exceptions import RedisError

from src.domains.knowledge.cache.redis_retrieval_cache import (
    RedisRetrievalCache,
)
from src.domains.knowledge.schemas.knowledge_retrieval_schema import (
    KnowledgeSearchResponse,
)


def build_response() -> KnowledgeSearchResponse:
    return KnowledgeSearchResponse(
        query="python developer",
        minimum_similarity=0.2,
        category="career",
        language="en",
        result_count=0,
        candidate_result_count=0,
        results=[],
        retriever_name="hybrid",
        reranker_name=None,
        reranker_model_name=None,
        embedding_provider=(
            "sentence-transformers"
        ),
        embedding_model_name=(
            "BAAI/bge-small-en-v1.5"
        ),
    )


def test_set_serializes_response() -> None:
    redis_client = MagicMock()

    cache = RedisRetrievalCache(
        redis_client=redis_client,
    )

    response = build_response()

    cache.set(
        key="knowledge:retrieval:test",
        value=response,
        ttl_seconds=60,
    )

    redis_client.set.assert_called_once_with(
        name="knowledge:retrieval:test",
        value=response.model_dump_json(),
        ex=60,
    )


def test_get_deserializes_response() -> None:
    redis_client = MagicMock()

    response = build_response()

    redis_client.get.return_value = (
        response.model_dump_json()
    )

    cache = RedisRetrievalCache(
        redis_client=redis_client,
    )

    cached_response = cache.get(
        "knowledge:retrieval:test"
    )

    assert cached_response == response


def test_get_returns_none_for_missing_key() -> None:
    redis_client = MagicMock()
    redis_client.get.return_value = None

    cache = RedisRetrievalCache(
        redis_client=redis_client,
    )

    assert (
        cache.get(
            "knowledge:retrieval:missing"
        )
        is None
    )


def test_get_deletes_invalid_payload() -> None:
    redis_client = MagicMock()
    redis_client.get.return_value = (
        "invalid-json"
    )

    cache = RedisRetrievalCache(
        redis_client=redis_client,
    )

    cached_response = cache.get(
        "knowledge:retrieval:test"
    )

    assert cached_response is None

    redis_client.delete.assert_called_once_with(
        "knowledge:retrieval:test"
    )


def test_delete_removes_key() -> None:
    redis_client = MagicMock()

    cache = RedisRetrievalCache(
        redis_client=redis_client,
    )

    cache.delete(
        "knowledge:retrieval:test"
    )

    redis_client.delete.assert_called_once_with(
        "knowledge:retrieval:test"
    )


def test_clear_deletes_only_retrieval_keys() -> None:
    redis_client = MagicMock()

    redis_client.scan_iter.return_value = [
        "knowledge:retrieval:first",
        "knowledge:retrieval:second",
    ]

    cache = RedisRetrievalCache(
        redis_client=redis_client,
    )

    cache.clear()

    redis_client.scan_iter.assert_called_once_with(
        match="knowledge:retrieval:*"
    )

    redis_client.delete.assert_called_once_with(
        "knowledge:retrieval:first",
        "knowledge:retrieval:second",
    )


def test_clear_does_not_delete_when_no_keys() -> None:
    redis_client = MagicMock()
    redis_client.scan_iter.return_value = []

    cache = RedisRetrievalCache(
        redis_client=redis_client,
    )

    cache.clear()

    redis_client.delete.assert_not_called()


def test_set_rejects_invalid_ttl() -> None:
    redis_client = MagicMock()

    cache = RedisRetrievalCache(
        redis_client=redis_client,
    )

    with pytest.raises(
        ValueError,
        match=(
            "ttl_seconds must be "
            "greater than zero"
        ),
    ):
        cache.set(
            key="knowledge:retrieval:test",
            value=build_response(),
            ttl_seconds=0,
        )


def test_get_returns_none_when_redis_fails() -> None:
    redis_client = MagicMock()

    redis_client.get.side_effect = RedisError(
        "Redis unavailable"
    )

    cache = RedisRetrievalCache(
        redis_client=redis_client,
    )

    assert (
        cache.get(
            "knowledge:retrieval:test"
        )
        is None
    )


def test_set_does_not_break_when_redis_fails() -> None:
    redis_client = MagicMock()

    redis_client.set.side_effect = RedisError(
        "Redis unavailable"
    )

    cache = RedisRetrievalCache(
        redis_client=redis_client,
    )

    cache.set(
        key="knowledge:retrieval:test",
        value=build_response(),
        ttl_seconds=60,
    )