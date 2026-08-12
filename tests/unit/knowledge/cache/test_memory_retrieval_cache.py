import pytest

import src.domains.knowledge.cache.memory_retrieval_cache as memory_cache_module
from src.domains.knowledge.cache.memory_retrieval_cache import (
    MemoryRetrievalCache,
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

def test_set_and_get_cached_response() -> None:
    cache = MemoryRetrievalCache()

    response = build_response()

    cache.set(
        key="knowledge:test",
        value=response,
        ttl_seconds=60,
    )

    cached_response = cache.get(
        "knowledge:test"
    )

    assert cached_response is not None
    assert cached_response == response


def test_get_returns_none_for_missing_key() -> None:
    cache = MemoryRetrievalCache()

    cached_response = cache.get(
        "missing-key"
    )

    assert cached_response is None


def test_delete_removes_cached_response() -> None:
    cache = MemoryRetrievalCache()

    cache.set(
        key="knowledge:test",
        value=build_response(),
        ttl_seconds=60,
    )

    cache.delete(
        "knowledge:test"
    )

    assert (
        cache.get("knowledge:test")
        is None
    )


def test_clear_removes_all_cached_responses() -> None:
    cache = MemoryRetrievalCache()

    cache.set(
        key="knowledge:first",
        value=build_response(),
        ttl_seconds=60,
    )

    cache.set(
        key="knowledge:second",
        value=build_response(),
        ttl_seconds=60,
    )

    cache.clear()

    assert (
        cache.get("knowledge:first")
        is None
    )

    assert (
        cache.get("knowledge:second")
        is None
    )


def test_expired_response_is_not_returned(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_time = 1000.0

    monkeypatch.setattr(
        memory_cache_module.time,
        "time",
        lambda: current_time,
    )

    cache = MemoryRetrievalCache()

    cache.set(
        key="knowledge:test",
        value=build_response(),
        ttl_seconds=60,
    )

    current_time = 1061.0

    cached_response = cache.get(
        "knowledge:test"
    )

    assert cached_response is None


def test_set_rejects_invalid_ttl() -> None:
    cache = MemoryRetrievalCache()

    with pytest.raises(
        ValueError,
        match=(
            "ttl_seconds must be "
            "greater than zero"
        ),
    ):
        cache.set(
            key="knowledge:test",
            value=build_response(),
            ttl_seconds=0,
        )