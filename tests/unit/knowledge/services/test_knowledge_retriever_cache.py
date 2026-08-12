from unittest.mock import MagicMock

import pytest

import src.domains.knowledge.services.knowledge_retriever as retriever_module
from src.domains.knowledge.schemas.knowledge_retrieval_schema import (
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
)
from src.domains.knowledge.services.knowledge_retriever import (
    KnowledgeRetriever,
)


def build_request(
    query: str = "  python   developer  ",
) -> KnowledgeSearchRequest:
    return KnowledgeSearchRequest(
        query=query,
        limit=10,
        minimum_similarity=0.2,
        category="career",
        language="en",
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
        reranker_name="cross-encoder",
        reranker_model_name=(
            "cross-encoder/"
            "ms-marco-MiniLM-L6-v2"
        ),
        embedding_provider=(
            "sentence-transformers"
        ),
        embedding_model_name=(
            "BAAI/bge-small-en-v1.5"
        ),
    )


@pytest.fixture
def dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> dict[str, MagicMock]:
    embedding_client = MagicMock()
    embedding_client.provider_name = (
        "sentence-transformers"
    )
    embedding_client.model_name = (
        "BAAI/bge-small-en-v1.5"
    )
    embedding_client.embed_text.return_value = [
        0.1,
        0.2,
    ]

    underlying_retriever = MagicMock()
    underlying_retriever.retriever_name = (
        "hybrid"
    )
    underlying_retriever.retrieve.return_value = []

    reranker = MagicMock()
    reranker.reranker_name = (
        "cross-encoder"
    )
    reranker.rerank.return_value = []

    monkeypatch.setattr(
        retriever_module,
        "get_embedding_client",
        lambda: embedding_client,
    )

    monkeypatch.setattr(
        retriever_module,
        "get_knowledge_retriever",
        lambda **kwargs: underlying_retriever,
    )

    monkeypatch.setattr(
        retriever_module,
        "get_knowledge_reranker",
        lambda: reranker,
    )

    monkeypatch.setattr(
        retriever_module.settings,
        "knowledge_retrieval_cache_enabled",
        True,
    )

    monkeypatch.setattr(
        retriever_module.settings,
        "knowledge_retrieval_cache_ttl_seconds",
        300,
    )

    return {
        "embedding_client": embedding_client,
        "underlying_retriever": (
            underlying_retriever
        ),
        "reranker": reranker,
    }


def test_cache_hit_skips_retrieval_pipeline(
    dependencies: dict[str, MagicMock],
) -> None:
    retrieval_cache = MagicMock()
    retrieval_cache.provider_name = (
        "redis"
    )
    cache_key_builder = MagicMock()

    cached_response = build_response()

    cache_key_builder.build.return_value = (
        "knowledge:retrieval:test"
    )
    retrieval_cache.get.return_value = (
        cached_response
    )

    service = KnowledgeRetriever(
        db=MagicMock(),
        retrieval_cache=retrieval_cache,
        cache_key_builder=cache_key_builder,
    )

    request = build_request()

    response = service.retrieve(request)

    assert response == cached_response

    cache_key_builder.build.assert_called_once()

    normalized_request = (
        cache_key_builder
        .build
        .call_args
        .args[0]
    )

    assert normalized_request.query == (
        "python developer"
    )

    retrieval_cache.get.assert_called_once_with(
        "knowledge:retrieval:test"
    )

    dependencies[
        "embedding_client"
    ].embed_text.assert_not_called()

    dependencies[
        "underlying_retriever"
    ].retrieve.assert_not_called()

    dependencies[
        "reranker"
    ].rerank.assert_not_called()

    retrieval_cache.set.assert_not_called()

def test_cache_hit_returns_observability_metadata(
    dependencies: dict[str, MagicMock],
) -> None:
    retrieval_cache = MagicMock()
    retrieval_cache.provider_name = (
        "redis"
    )

    cache_key_builder = MagicMock()

    cached_response = build_response()

    cache_key_builder.build.return_value = (
        "knowledge:retrieval:test"
    )

    retrieval_cache.get.return_value = (
        cached_response
    )

    service = KnowledgeRetriever(
        db=MagicMock(),
        retrieval_cache=retrieval_cache,
        cache_key_builder=cache_key_builder,
    )

    execution = (
        service
        .retrieve_with_observability(
            build_request()
        )
    )

    assert execution.response == (
        cached_response
    )

    assert execution.cache_enabled is True
    assert execution.cache_hit is True

    assert execution.cache_provider == (
        "redis"
    )

    assert (
        execution
        .cache_read_latency_ms
        is not None
    )

    assert (
        execution
        .cache_read_latency_ms
        >= 0.0
    )

    assert (
        execution
        .cache_write_latency_ms
        is None
    )

    retrieval_cache.set.assert_not_called()

def test_cache_miss_runs_pipeline_and_caches_response(
    dependencies: dict[str, MagicMock],
) -> None:
    retrieval_cache = MagicMock()
    retrieval_cache.provider_name = (
        "redis"
    )
    cache_key_builder = MagicMock()

    cache_key_builder.build.return_value = (
        "knowledge:retrieval:test"
    )
    retrieval_cache.get.return_value = None

    service = KnowledgeRetriever(
        db=MagicMock(),
        retrieval_cache=retrieval_cache,
        cache_key_builder=cache_key_builder,
    )

    request = build_request()

    response = service.retrieve(request)

    assert response.query == (
        "python developer"
    )
    assert response.result_count == 0
    assert response.candidate_result_count == 0

    dependencies[
        "embedding_client"
    ].embed_text.assert_called_once_with(
        "python developer"
    )

    dependencies[
        "underlying_retriever"
    ].retrieve.assert_called_once_with(
        query_text="python developer",
        query_embedding=[0.1, 0.2],
        limit=30,
        minimum_similarity=0.2,
        category="career",
        language="en",
    )

    dependencies[
        "reranker"
    ].rerank.assert_called_once_with(
        query_text="python developer",
        results=[],
        limit=10,
        minimum_score=(
            retriever_module
            .settings
            .knowledge_reranker_minimum_score
        ),
    )

    retrieval_cache.set.assert_called_once_with(
        key="knowledge:retrieval:test",
        value=response,
        ttl_seconds=300,
    )

def test_cache_miss_returns_observability_metadata(
    dependencies: dict[str, MagicMock],
) -> None:
    retrieval_cache = MagicMock()
    retrieval_cache.provider_name = (
        "redis"
    )

    cache_key_builder = MagicMock()

    cache_key_builder.build.return_value = (
        "knowledge:retrieval:test"
    )

    retrieval_cache.get.return_value = None

    service = KnowledgeRetriever(
        db=MagicMock(),
        retrieval_cache=retrieval_cache,
        cache_key_builder=cache_key_builder,
    )

    execution = (
        service
        .retrieve_with_observability(
            build_request()
        )
    )

    assert execution.cache_enabled is True
    assert execution.cache_hit is False

    assert execution.cache_provider == (
        "redis"
    )

    assert (
        execution
        .cache_read_latency_ms
        is not None
    )

    assert (
        execution
        .cache_read_latency_ms
        >= 0.0
    )

    assert (
        execution
        .cache_write_latency_ms
        is not None
    )

    assert (
        execution
        .cache_write_latency_ms
        >= 0.0
    )

    retrieval_cache.set.assert_called_once()

def test_disabled_cache_returns_empty_cache_metadata(
    dependencies: dict[str, MagicMock],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        retriever_module.settings,
        "knowledge_retrieval_cache_enabled",
        False,
    )

    service = KnowledgeRetriever(
        db=MagicMock(),
    )

    execution = (
        service
        .retrieve_with_observability(
            build_request()
        )
    )

    assert execution.cache_enabled is False
    assert execution.cache_hit is None
    assert execution.cache_provider is None

    assert (
        execution
        .cache_read_latency_ms
        is None
    )

    assert (
        execution
        .cache_write_latency_ms
        is None
    )