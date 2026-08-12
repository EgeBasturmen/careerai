from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from src.domains.knowledge.models.rag_run import (
    RAGRun,
)
from src.domains.knowledge.models.rag_run_chunk import (
    RAGRunChunk,
)
from sqlalchemy import func
from sqlalchemy.orm import (
    Session,
    selectinload,
)
from datetime import datetime
from typing import Any

from sqlalchemy import case, func
from sqlalchemy.orm import (
    Session,
    selectinload,
)

class RAGRunRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create_run(
        self,
        *,
        user_id: int,
        question: str,
        category: str | None,
        language: str | None,
        retrieval_limit: int,
        minimum_similarity: float,
        prompt_name: str,
        prompt_version: str,
        llm_provider: str | None,
        llm_model_name: str | None,
    ) -> RAGRun:
        rag_run = RAGRun(
            user_id=user_id,
            question=question,
            category=category,
            language=language,
            retrieval_limit=retrieval_limit,
            minimum_similarity=(
                minimum_similarity
            ),
            prompt_name=prompt_name,
            prompt_version=prompt_version,
            llm_provider=llm_provider,
            llm_model_name=llm_model_name,
            generation_status="PROCESSING",
        )

        self.db.add(
            rag_run
        )

        self.db.flush()

        return rag_run

    def add_chunk(
        self,
        *,
        rag_run_id: int,
        knowledge_chunk_id: int,
        knowledge_document_id: int,
        source_number: int,
        retrieval_rank: int,
        chunk_index: int,
        document_title: str,
        chunk_content: str,
        similarity_score: float,
        was_included_in_context: bool,
        chunk_metadata: dict[str, Any],
    ) -> RAGRunChunk:
        rag_run_chunk = RAGRunChunk(
            rag_run_id=rag_run_id,
            knowledge_chunk_id=(
                knowledge_chunk_id
            ),
            knowledge_document_id=(
                knowledge_document_id
            ),
            source_number=source_number,
            retrieval_rank=retrieval_rank,
            chunk_index=chunk_index,
            document_title=document_title,
            chunk_content=chunk_content,
            similarity_score=similarity_score,
            was_included_in_context=(
                was_included_in_context
            ),
            was_cited=False,
            chunk_metadata=chunk_metadata,
        )

        self.db.add(
            rag_run_chunk
        )

        return rag_run_chunk

    def mark_cited_sources(
        self,
        *,
        rag_run_id: int,
        cited_source_numbers: set[int],
    ) -> None:
        if not cited_source_numbers:
            return

        (
            self.db.query(
                RAGRunChunk
            )
            .filter(
                RAGRunChunk.rag_run_id
                == rag_run_id,
                RAGRunChunk.source_number.in_(
                    cited_source_numbers
                ),
            )
            .update(
                {
                    RAGRunChunk.was_cited: True,
                },
                synchronize_session=False,
            )
        )

    def complete_run(
        self,
        *,
        rag_run: RAGRun,
        generation_status: str,
        answer: str,
        sufficient_context: bool,
        confidence: float,
        candidate_result_count: int,
        retrieval_result_count: int,
        retriever_name: str | None,
        reranker_name: str | None,
        reranker_model_name: str | None,
        context_source_count: int,
        context_character_count: int,
        embedding_provider: str | None,
        embedding_model_name: str | None,
        retrieval_latency_ms: float,
        context_build_latency_ms: float,
        prompt_build_latency_ms: float,
        original_query: str,
        rewritten_query: str,
        was_rewritten: bool,

        rewrite_provider: str | None,
        rewrite_model_name: str | None,

        rewrite_latency_ms: float,

        rewrite_fallback_used: bool,
        rewrite_fallback_reason: str | None,
        llm_latency_ms: float,
        total_latency_ms: float,
        citations: list[dict[str, Any]],
        validation_errors: list[str],
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
        total_tokens: int | None = None,
        cache_enabled: bool,
        cache_hit: bool | None,
        cache_provider: str | None,

        cache_read_latency_ms: float | None,
        cache_write_latency_ms: float | None,
    ) -> RAGRun:
        rag_run.generation_status = (
            generation_status
        )

        rag_run.answer = answer

        rag_run.sufficient_context = (
            sufficient_context
        )

        rag_run.confidence = confidence

        rag_run.candidate_result_count = (
            candidate_result_count
        )

        rag_run.retrieval_result_count = (
            retrieval_result_count
        )

        rag_run.retriever_name = (
            retriever_name
        )

        rag_run.reranker_name = (
            reranker_name
        )

        rag_run.reranker_model_name = (
            reranker_model_name
        )

        rag_run.context_source_count = (
            context_source_count
        )

        rag_run.context_character_count = (
            context_character_count
        )

        rag_run.embedding_provider = (
            embedding_provider
        )

        rag_run.embedding_model_name = (
            embedding_model_name
        )
        rag_run.original_query = (
            original_query
        )

        rag_run.rewritten_query = (
            rewritten_query
        )

        rag_run.was_rewritten = (
            was_rewritten
        )

        rag_run.rewrite_provider = (
            rewrite_provider
        )

        rag_run.rewrite_model_name = (
            rewrite_model_name
        )

        rag_run.rewrite_latency_ms = (
            rewrite_latency_ms
        )

        rag_run.rewrite_fallback_used = (
            rewrite_fallback_used
        )

        rag_run.rewrite_fallback_reason = (
            rewrite_fallback_reason
        )

        rag_run.retrieval_latency_ms = (
            retrieval_latency_ms
        )

        rag_run.cache_enabled = cache_enabled

        rag_run.cache_hit = cache_hit

        rag_run.cache_provider = cache_provider

        rag_run.cache_read_latency_ms = (
            cache_read_latency_ms
        )

        rag_run.cache_write_latency_ms = (
            cache_write_latency_ms
        )

        rag_run.context_build_latency_ms = (
            context_build_latency_ms
        )

        rag_run.prompt_build_latency_ms = (
            prompt_build_latency_ms
        )

        rag_run.llm_latency_ms = (
            llm_latency_ms
        )

        rag_run.total_latency_ms = (
            total_latency_ms
        )

        rag_run.citations = citations

        rag_run.validation_errors = (
            validation_errors
        )

        rag_run.prompt_tokens = (
            prompt_tokens
        )

        rag_run.completion_tokens = (
            completion_tokens
        )

        rag_run.total_tokens = (
            total_tokens
        )

        rag_run.error_type = None
        rag_run.error_message = None

        rag_run.completed_at = (
            datetime.utcnow()
        )

        self.db.flush()

        return rag_run

    def fail_run(
        self,
        *,
        rag_run: RAGRun,
        error: Exception,
        total_latency_ms: float,
        retrieval_latency_ms: float | None = None,
        context_build_latency_ms: (
            float | None
        ) = None,
        prompt_build_latency_ms: (
            float | None
        ) = None,
        llm_latency_ms: float | None = None,
        cache_enabled: bool = False,
        cache_hit: bool | None = None,
        cache_provider: str | None = None,
        cache_read_latency_ms: float | None = None,
        cache_write_latency_ms: float | None = None,
    ) -> RAGRun:
        rag_run.generation_status = "FAILED"

        rag_run.error_type = type(
            error
        ).__name__

        rag_run.error_message = str(
            error
        )[:5000]

        rag_run.total_latency_ms = (
            total_latency_ms
        )

        rag_run.retrieval_latency_ms = (
            retrieval_latency_ms
        )

        rag_run.context_build_latency_ms = (
            context_build_latency_ms
        )

        rag_run.prompt_build_latency_ms = (
            prompt_build_latency_ms
        )
        rag_run.retrieval_latency_ms = (
            retrieval_latency_ms
        )

        rag_run.cache_enabled = (
            cache_enabled
        )

        rag_run.cache_hit = (
            cache_hit
        )

        rag_run.cache_provider = (
            cache_provider
        )

        rag_run.cache_read_latency_ms = (
            cache_read_latency_ms
        )

        rag_run.cache_write_latency_ms = (
            cache_write_latency_ms
        )

        rag_run.context_build_latency_ms = (
            context_build_latency_ms
        )

        rag_run.llm_latency_ms = (
            llm_latency_ms
        )

        rag_run.cache_enabled = (
            cache_enabled
        )

        rag_run.cache_hit = (
            cache_hit
        )

        rag_run.cache_provider = (
            cache_provider
        )

        rag_run.cache_read_latency_ms = (
            cache_read_latency_ms
        )

        rag_run.cache_write_latency_ms = (
            cache_write_latency_ms
        )

        rag_run.completed_at = datetime.utcnow()

        self.db.flush()

        return rag_run

    def get_by_id(
        self,
        rag_run_id: int,
        user_id: int,
    ) -> RAGRun | None:
        return (
            self.db.query(
                RAGRun
            )
            .filter(
                RAGRun.id == rag_run_id,
                RAGRun.user_id == user_id,
            )
            .first()
        )


    

    def get_detail_by_id(
        self,
        *,
        rag_run_id: int,
        user_id: int,
    ) -> RAGRun | None:
        return (
            self.db.query(
                RAGRun
            )
            .options(
                selectinload(
                    RAGRun.chunks
                )
            )
            .filter(
                RAGRun.id == rag_run_id,
                RAGRun.user_id == user_id,
            )
            .first()
        )

    def count_by_user(
        self,
        *,
        user_id: int,
        generation_status: str | None = None,
    ) -> int:
        query = (
            self.db.query(
                func.count(
                    RAGRun.id
                )
            )
            .filter(
                RAGRun.user_id == user_id
            )
        )

        if generation_status:
            query = query.filter(
                RAGRun.generation_status
                == generation_status
            )

        return int(
            query.scalar()
            or 0
        )

    def list_by_user(
        self,
        *,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
        generation_status: str | None = None,
    ) -> list[RAGRun]:
        query = (
            self.db.query(
                RAGRun
            )
            .filter(
                RAGRun.user_id == user_id
            )
        )

        if generation_status:
            query = query.filter(
                RAGRun.generation_status
                == generation_status
            )

        return (
            query
            .order_by(
                RAGRun.created_at.desc(),
                RAGRun.id.desc(),
            )
            .offset(offset)
            .limit(limit)
            .all()
        )
    
    def get_statistics(
        self,
        *,
        user_id: int,
        created_after: datetime | None = None,
    ) -> dict[str, Any]:
        query = (
            self.db.query(
                func.count(
                    RAGRun.id
                ).label(
                    "total_runs"
                ),
                func.sum(
                    case(
                        (
                            RAGRun.generation_status
                            == "SUCCESS",
                            1,
                        ),
                        else_=0,
                    )
                ).label(
                    "success_runs"
                ),
                func.sum(
                    case(
                        (
                            RAGRun.generation_status
                            == "FAILED",
                            1,
                        ),
                        else_=0,
                    )
                ).label(
                    "failed_runs"
                ),
                func.sum(
                    case(
                        (
                            RAGRun.generation_status
                            == "NO_CONTEXT",
                            1,
                        ),
                        else_=0,
                    )
                ).label(
                    "no_context_runs"
                ),
                func.sum(
                    case(
                        (
                            RAGRun.generation_status
                            == "INVALID_GENERATION",
                            1,
                        ),
                        else_=0,
                    )
                ).label(
                    "invalid_generation_runs"
                ),
                func.sum(
                    case(
                        (
                            RAGRun.generation_status
                            == "PROCESSING",
                            1,
                        ),
                        else_=0,
                    )
                ).label(
                    "processing_runs"
                ),

                func.sum(
                    case(
                        (
                            RAGRun.cache_enabled.is_(True),
                            1,
                        ),
                        else_=0,
                    )
                ).label(
                    "cache_enabled_runs"
                ),

                func.sum(
                    case(
                        (
                            RAGRun.cache_hit.is_(True),
                            1,
                        ),
                        else_=0,
                    )
                ).label(
                    "cache_hit_runs"
                ),

                func.sum(
                    case(
                        (
                            RAGRun.cache_hit.is_(False),
                            1,
                        ),
                        else_=0,
                    )
                ).label(
                    "cache_miss_runs"
                ),

                func.avg(
                    RAGRun.cache_read_latency_ms
                ).label(
                    "average_cache_read_latency_ms"
                ),

                func.avg(
                    RAGRun.cache_write_latency_ms
                ).label(
                    "average_cache_write_latency_ms"
                ),

                func.avg(
                    case(
                        (
                            RAGRun.cache_hit.is_(True),
                            RAGRun.retrieval_latency_ms,
                        ),
                        else_=None,
                    )
                ).label(
                    "average_cache_hit_retrieval_latency_ms"
                ),

                func.avg(
                    case(
                        (
                            RAGRun.cache_hit.is_(False),
                            RAGRun.retrieval_latency_ms,
                        ),
                        else_=None,
                    )
                ).label(
                    "average_cache_miss_retrieval_latency_ms"
                ),
                func.avg(
                    RAGRun
                    .retrieval_latency_ms
                ).label(
                    "average_retrieval_latency_ms"
                ),
                func.avg(
                    RAGRun
                    .context_build_latency_ms
                ).label(
                    "average_context_build_latency_ms"
                ),
                func.avg(
                    RAGRun
                    .prompt_build_latency_ms
                ).label(
                    "average_prompt_build_latency_ms"
                ),
                func.avg(
                    RAGRun
                    .llm_latency_ms
                ).label(
                    "average_llm_latency_ms"
                ),
                func.avg(
                    RAGRun
                    .total_latency_ms
                ).label(
                    "average_total_latency_ms"
                ),
                func.avg(
                    RAGRun
                    .context_source_count
                ).label(
                    "average_context_source_count"
                ),
                func.avg(
                    RAGRun.confidence
                ).label(
                    "average_confidence"
                ),
            )
            .filter(
                RAGRun.user_id == user_id
            )
        )

        if created_after is not None:
            query = query.filter(
                RAGRun.created_at
                >= created_after
            )

        row = query.one()

        return {
            "total_runs": int(
                row.total_runs or 0
            ),
            "success_runs": int(
                row.success_runs or 0
            ),
            "failed_runs": int(
                row.failed_runs or 0
            ),
            "no_context_runs": int(
                row.no_context_runs or 0
            ),
            "invalid_generation_runs": int(
                row.invalid_generation_runs
                or 0
            ),
            "processing_runs": int(
                row.processing_runs or 0
            ),
            "average_retrieval_latency_ms": (
                float(
                    row
                    .average_retrieval_latency_ms
                    or 0.0
                )
            ),
            "average_context_build_latency_ms": (
                float(
                    row
                    .average_context_build_latency_ms
                    or 0.0
                )
            ),
            "average_prompt_build_latency_ms": (
                float(
                    row
                    .average_prompt_build_latency_ms
                    or 0.0
                )
            ),
            "average_llm_latency_ms": float(
                row.average_llm_latency_ms
                or 0.0
            ),
            "average_total_latency_ms": float(
                row.average_total_latency_ms
                or 0.0
            ),
            "average_context_source_count": (
                float(
                    row
                    .average_context_source_count
                    or 0.0
                )
            ),
            "average_confidence": (
                float(
                    row.average_confidence
                )
                if row.average_confidence
                is not None
                else None
            ),

            "cache_enabled_runs": int(
                row.cache_enabled_runs or 0
            ),

            "cache_hit_runs": int(
                row.cache_hit_runs or 0
            ),

            "cache_miss_runs": int(
                row.cache_miss_runs or 0
            ),

            "average_cache_read_latency_ms": (
                float(
                    row.average_cache_read_latency_ms
                    or 0.0
                )
            ),

            "average_cache_write_latency_ms": (
                float(
                    row.average_cache_write_latency_ms
                    or 0.0
                )
            ),

            "average_cache_hit_retrieval_latency_ms": (
                float(
                    row
                    .average_cache_hit_retrieval_latency_ms
                    or 0.0
                )
            ),

            "average_cache_miss_retrieval_latency_ms": (
                float(
                    row
                    .average_cache_miss_retrieval_latency_ms
                    or 0.0
                )
            ),
        }

    def count_success_runs_with_citations(
        self,
        *,
        user_id: int,
        created_after: datetime | None = None,
    ) -> int:
        query = (
            self.db.query(
                func.count(
                    RAGRun.id
                )
            )
            .filter(
                RAGRun.user_id == user_id,
                RAGRun.generation_status
                == "SUCCESS",
                func.jsonb_array_length(
                    RAGRun.citations
                )
                > 0,
            )
        )

        if created_after is not None:
            query = query.filter(
                RAGRun.created_at
                >= created_after
            )

        return int(
            query.scalar() or 0
        )

    def list_top_errors(
        self,
        *,
        user_id: int,
        limit: int = 5,
        created_after: datetime | None = None,
    ) -> list[tuple[str, int]]:
        query = (
            self.db.query(
                RAGRun.error_type,
                func.count(
                    RAGRun.id
                ).label(
                    "error_count"
                ),
            )
            .filter(
                RAGRun.user_id == user_id,
                RAGRun.error_type.is_not(
                    None
                ),
            )
        )

        if created_after is not None:
            query = query.filter(
                RAGRun.created_at
                >= created_after
            )

        rows = (
            query
            .group_by(
                RAGRun.error_type
            )
            .order_by(
                func.count(
                    RAGRun.id
                ).desc()
            )
            .limit(limit)
            .all()
        )

        return [
            (
                str(error_type),
                int(error_count),
            )
            for (
                error_type,
                error_count,
            ) in rows
        ]

    def get_by_id_for_evaluation(
        self,
        *,
        rag_run_id: int,
    ) -> RAGRun | None:
        return (
            self.db.query(
                RAGRun
            )
            .options(
                selectinload(
                    RAGRun.chunks
                ),
                selectinload(
                    RAGRun.answer_evaluations
                ),
            )
            .filter(
                RAGRun.id == rag_run_id,
            )
            .first()
        )