from unittest.mock import Mock

import pytest

from src.domains.knowledge.services.rag_statistics_service import (
    RAGStatisticsService,
)


@pytest.fixture
def repository_statistics() -> dict:
    return {
        "total_runs": 10,
        "success_runs": 7,
        "failed_runs": 1,
        "no_context_runs": 1,
        "invalid_generation_runs": 1,
        "processing_runs": 0,

        "average_retrieval_latency_ms": 40.0,
        "average_context_build_latency_ms": 5.0,
        "average_prompt_build_latency_ms": 2.0,
        "average_llm_latency_ms": 300.0,
        "average_total_latency_ms": 350.0,
        "average_context_source_count": 3.0,
        "average_confidence": 0.85,

        "cache_enabled_runs": 8,
        "cache_hit_runs": 5,
        "cache_miss_runs": 3,

        "average_cache_read_latency_ms": 1.4,
        "average_cache_write_latency_ms": 2.8,

        "average_cache_hit_retrieval_latency_ms": (
            5.0
        ),
        "average_cache_miss_retrieval_latency_ms": (
            95.0
        ),
    }


def build_service(
    repository_statistics: dict,
    *,
    success_runs_with_citations: int = 0,
) -> tuple[RAGStatisticsService, Mock]:
    repository = Mock()

    repository.get_statistics.return_value = (
        repository_statistics
    )

    repository.count_success_runs_with_citations.return_value = (
        success_runs_with_citations
    )

    repository.list_top_errors.return_value = []

    service = RAGStatisticsService.__new__(
        RAGStatisticsService
    )

    service.repository = repository

    return service, repository


def test_get_statistics_calculates_cache_metrics(
    repository_statistics: dict,
) -> None:
    service, repository = build_service(
        repository_statistics,
        success_runs_with_citations=5,
    )

    result = service.get_statistics(
        user_id=1,
    )

    assert result.cache_enabled_runs == 8
    assert result.cache_hit_runs == 5
    assert result.cache_miss_runs == 3

    assert result.cache_hit_rate == 62.5
    assert result.cache_miss_rate == 37.5

    assert (
        result.average_cache_read_latency_ms
        == 1.4
    )

    assert (
        result.average_cache_write_latency_ms
        == 2.8
    )

    assert (
        result
        .average_cache_hit_retrieval_latency_ms
        == 5.0
    )

    assert (
        result
        .average_cache_miss_retrieval_latency_ms
        == 95.0
    )

    assert (
        result
        .estimated_retrieval_latency_saved_ms
        == 90.0
    )

    repository.get_statistics.assert_called_once_with(
        user_id=1,
        created_after=None,
    )

    (
        repository
        .count_success_runs_with_citations
        .assert_called_once_with(
            user_id=1,
            created_after=None,
        )
    )

    repository.list_top_errors.assert_called_once_with(
        user_id=1,
        limit=5,
        created_after=None,
    )


def test_get_statistics_handles_zero_cache_runs(
) -> None:
    statistics = {
        "total_runs": 0,
        "success_runs": 0,
        "failed_runs": 0,
        "no_context_runs": 0,
        "invalid_generation_runs": 0,
        "processing_runs": 0,

        "average_retrieval_latency_ms": 0.0,
        "average_context_build_latency_ms": 0.0,
        "average_prompt_build_latency_ms": 0.0,
        "average_llm_latency_ms": 0.0,
        "average_total_latency_ms": 0.0,
        "average_context_source_count": 0.0,
        "average_confidence": None,

        "cache_enabled_runs": 0,
        "cache_hit_runs": 0,
        "cache_miss_runs": 0,

        "average_cache_read_latency_ms": 0.0,
        "average_cache_write_latency_ms": 0.0,

        "average_cache_hit_retrieval_latency_ms": (
            0.0
        ),
        "average_cache_miss_retrieval_latency_ms": (
            0.0
        ),
    }

    service, repository = build_service(
        statistics
    )

    result = service.get_statistics(
        user_id=1,
    )

    assert result.cache_enabled_runs == 0
    assert result.cache_hit_runs == 0
    assert result.cache_miss_runs == 0

    assert result.cache_hit_rate == 0.0
    assert result.cache_miss_rate == 0.0

    assert (
        result
        .estimated_retrieval_latency_saved_ms
        == 0.0
    )

    repository.get_statistics.assert_called_once_with(
        user_id=1,
        created_after=None,
    )


def test_latency_saved_never_becomes_negative(
) -> None:
    statistics = {
        "total_runs": 2,
        "success_runs": 2,
        "failed_runs": 0,
        "no_context_runs": 0,
        "invalid_generation_runs": 0,
        "processing_runs": 0,

        "average_retrieval_latency_ms": 10.0,
        "average_context_build_latency_ms": 1.0,
        "average_prompt_build_latency_ms": 1.0,
        "average_llm_latency_ms": 10.0,
        "average_total_latency_ms": 22.0,
        "average_context_source_count": 2.0,
        "average_confidence": 0.9,

        "cache_enabled_runs": 2,
        "cache_hit_runs": 1,
        "cache_miss_runs": 1,

        "average_cache_read_latency_ms": 1.0,
        "average_cache_write_latency_ms": 1.0,

        "average_cache_hit_retrieval_latency_ms": (
            20.0
        ),
        "average_cache_miss_retrieval_latency_ms": (
            10.0
        ),
    }

    service, repository = build_service(
        statistics
    )

    result = service.get_statistics(
        user_id=1,
    )

    assert (
        result
        .estimated_retrieval_latency_saved_ms
        == 0.0
    )

    repository.get_statistics.assert_called_once_with(
        user_id=1,
        created_after=None,
    )