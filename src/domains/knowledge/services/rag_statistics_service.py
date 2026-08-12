from datetime import (
    datetime,
    timedelta,
)

from sqlalchemy.orm import Session

from src.domains.knowledge.repositories.rag_run_repository import (
    RAGRunRepository,
)
from src.domains.knowledge.schemas.rag_statistics_schema import (
    RAGErrorStatisticResponse,
    RAGStatisticsResponse,
)


class RAGStatisticsService:
    def __init__(
        self,
        db: Session,
    ):
        self.repository = (
            RAGRunRepository(
                db
            )
        )

    def get_statistics(
        self,
        *,
        user_id: int,
        hours: int | None = None,
    ) -> RAGStatisticsResponse:
        created_after = (
            self._build_created_after(
                hours
            )
        )

        statistics = (
            self.repository
            .get_statistics(
                user_id=user_id,
                created_after=(
                    created_after
                ),
            )
        )

        success_with_citations = (
            self.repository
            .count_success_runs_with_citations(
                user_id=user_id,
                created_after=(
                    created_after
                ),
            )
        )

        top_error_rows = (
            self.repository
            .list_top_errors(
                user_id=user_id,
                limit=5,
                created_after=(
                    created_after
                ),
            )
        )

        total_runs = statistics[
            "total_runs"
        ]

        success_runs = statistics[
            "success_runs"
        ]

        failed_runs = statistics[
            "failed_runs"
        ]

        no_context_runs = statistics[
            "no_context_runs"
        ]

        invalid_generation_runs = (
            statistics[
                "invalid_generation_runs"
            ]
        )

        cache_enabled_runs = (
            statistics["cache_enabled_runs"]
        )

        cache_hit_runs = (
            statistics["cache_hit_runs"]
        )

        cache_miss_runs = (
            statistics["cache_miss_runs"]
        )

        cache_hit_rate = (
            self._percentage(
                cache_hit_runs,
                cache_enabled_runs,
            )
        )

        cache_miss_rate = (
            self._percentage(
                cache_miss_runs,
                cache_enabled_runs,
            )
        )

        average_cache_hit_retrieval_latency_ms = (
            statistics[
                "average_cache_hit_retrieval_latency_ms"
            ]
        )

        average_cache_miss_retrieval_latency_ms = (
            statistics[
                "average_cache_miss_retrieval_latency_ms"
            ]
        )

        estimated_retrieval_latency_saved_ms = max(
            0.0,
            (
                average_cache_miss_retrieval_latency_ms
                - average_cache_hit_retrieval_latency_ms
            ),
        )

        return RAGStatisticsResponse(
            total_runs=total_runs,
            success_runs=success_runs,
            failed_runs=failed_runs,
            no_context_runs=(
                no_context_runs
            ),
            invalid_generation_runs=(
                invalid_generation_runs
            ),
            processing_runs=statistics[
                "processing_runs"
            ],
            success_rate=self._percentage(
                success_runs,
                total_runs,
            ),
            failure_rate=self._percentage(
                failed_runs,
                total_runs,
            ),
            no_context_rate=(
                self._percentage(
                    no_context_runs,
                    total_runs,
                )
            ),
            invalid_generation_rate=(
                self._percentage(
                    invalid_generation_runs,
                    total_runs,
                )
            ),
            average_retrieval_latency_ms=(
                self._round_metric(
                    statistics[
                        "average_retrieval_latency_ms"
                    ]
                )
            ),
            average_context_build_latency_ms=(
                self._round_metric(
                    statistics[
                        "average_context_build_latency_ms"
                    ]
                )
            ),
            average_prompt_build_latency_ms=(
                self._round_metric(
                    statistics[
                        "average_prompt_build_latency_ms"
                    ]
                )
            ),
            average_llm_latency_ms=(
                self._round_metric(
                    statistics[
                        "average_llm_latency_ms"
                    ]
                )
            ),
            average_total_latency_ms=(
                self._round_metric(
                    statistics[
                        "average_total_latency_ms"
                    ]
                )
            ),
            average_context_source_count=(
                self._round_metric(
                    statistics[
                        "average_context_source_count"
                    ]
                )
            ),
            citation_rate=(
                self._percentage(
                    success_with_citations,
                    success_runs,
                )
            ),
            average_confidence=(
                self._round_metric(
                    statistics[
                        "average_confidence"
                    ]
                )
                if statistics[
                    "average_confidence"
                ]
                is not None
                else None
            ),

            cache_enabled_runs=(
                cache_enabled_runs
            ),

            cache_hit_runs=(
                cache_hit_runs
            ),

            cache_miss_runs=(
                cache_miss_runs
            ),

            cache_hit_rate=(
                self._round_metric(
                    cache_hit_rate
                )
            ),

            cache_miss_rate=(
                self._round_metric(
                    cache_miss_rate
                )
            ),

            average_cache_read_latency_ms=(
                self._round_metric(
                    statistics[
                        "average_cache_read_latency_ms"
                    ]
                )
            ),

            average_cache_write_latency_ms=(
                self._round_metric(
                    statistics[
                        "average_cache_write_latency_ms"
                    ]
                )
            ),

            average_cache_hit_retrieval_latency_ms=(
                self._round_metric(
                    average_cache_hit_retrieval_latency_ms
                )
            ),

            average_cache_miss_retrieval_latency_ms=(
                self._round_metric(
                    average_cache_miss_retrieval_latency_ms
                )
            ),

            estimated_retrieval_latency_saved_ms=(
                self._round_metric(
                    estimated_retrieval_latency_saved_ms
                )
            ),
            top_errors=[
                RAGErrorStatisticResponse(
                    error_type=error_type,
                    count=count,
                )
                for (
                    error_type,
                    count,
                ) in top_error_rows
            ],
        )

    def _build_created_after(
        self,
        hours: int | None,
    ) -> datetime | None:
        if hours is None:
            return None

        return datetime.utcnow() - timedelta(
            hours=hours
        )

    def _percentage(
        self,
        value: int,
        total: int,
    ) -> float:
        if total == 0:
            return 0.0

        return round(
            (
                value
                / total
            )
            * 100,
            2,
        )

    def _round_metric(
        self,
        value: float,
    ) -> float:
        return round(
            value,
            2,
        )