from typing import Any

from sqlalchemy.orm import Session

from src.domains.knowledge.models.rag_run import (
    RAGRun,
)
from src.domains.knowledge.rag.rag_context import (
    RAGContext,
)
from src.domains.knowledge.repositories.rag_run_repository import (
    RAGRunRepository,
)


class RAGRunRecorder:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

        self.repository = RAGRunRepository(
            db
        )

    def start(
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
        rag_run = self.repository.create_run(
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
        )

        self.db.commit()
        self.db.refresh(
            rag_run
        )

        return rag_run

    def record_context_chunks(
        self,
        *,
        rag_run: RAGRun,
        context: RAGContext,
    ) -> None:
        for retrieval_rank, item in enumerate(
            context.items,
            start=1,
        ):
            self.repository.add_chunk(
                rag_run_id=rag_run.id,
                knowledge_chunk_id=(
                    item.chunk_id
                ),
                knowledge_document_id=(
                    item.document_id
                ),
                source_number=(
                    item.source_number
                ),
                retrieval_rank=(
                    retrieval_rank
                ),
                chunk_index=item.chunk_index,
                document_title=(
                    item.document_title
                ),
                chunk_content=item.content,
                similarity_score=(
                    item.similarity_score
                ),
                was_included_in_context=True,
                chunk_metadata={
                    "category": item.category,
                    "language": item.language,
                    "source_type": (
                        item.source_type
                    ),
                    "source_uri": (
                        item.source_uri
                    ),
                },
            )

        self.db.flush()

    def complete(
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
        context: RAGContext,
        embedding_provider: str | None,
        embedding_model_name: str | None,
        original_query: str,
        rewritten_query: str,
        was_rewritten: bool,

        rewrite_provider: str | None,
        rewrite_model_name: str | None,

        rewrite_latency_ms: float,

        rewrite_fallback_used: bool,
        rewrite_fallback_reason: str | None,
        retrieval_latency_ms: float,
        context_build_latency_ms: float,
        prompt_build_latency_ms: float,
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
        cache_write_latency_ms: float |None,
    ) -> RAGRun:
        cited_source_numbers = {
            citation["source_number"]
            for citation in citations
            if "source_number" in citation
        }

        self.repository.mark_cited_sources(
            rag_run_id=rag_run.id,
            cited_source_numbers=(
                cited_source_numbers
            ),
        )

        try:
            completed_run = (
                self.repository.complete_run(
                    rag_run=rag_run,
                    generation_status=(
                        generation_status
                    ),
                    answer=answer,
                    sufficient_context=(
                        sufficient_context
                    ),
                    confidence=confidence,
                    candidate_result_count=(
                        candidate_result_count
                    ),
                    retrieval_result_count=(
                        retrieval_result_count
                    ),
                    retriever_name=(
                        retriever_name
                    ),
                    reranker_name=(
                        reranker_name
                    ),
                    reranker_model_name=(
                        reranker_model_name
                    ),
                    context_source_count=(
                        context.source_count
                    ),
                    context_character_count=(
                        context.character_count
                    ),
                    embedding_provider=(
                        embedding_provider
                    ),
                    embedding_model_name=(
                        embedding_model_name
                    ),
                    original_query=original_query,
                    rewritten_query=rewritten_query,
                    was_rewritten=was_rewritten,
                    rewrite_provider=(
                        rewrite_provider
                    ),
                    rewrite_model_name=(
                        rewrite_model_name
                    ),
                    rewrite_latency_ms=(
                        rewrite_latency_ms
                    ),
                    rewrite_fallback_used=(
                        rewrite_fallback_used
                    ),
                    rewrite_fallback_reason=(
                        rewrite_fallback_reason
                    ),
                    retrieval_latency_ms=(
                        retrieval_latency_ms
                    ),
                    context_build_latency_ms=(
                        context_build_latency_ms
                    ),
                    prompt_build_latency_ms=(
                        prompt_build_latency_ms
                    ),
                    llm_latency_ms=(
                        llm_latency_ms
                    ),
                    cache_enabled=(
                        cache_enabled
                    ),
                    cache_hit=cache_hit,
                    cache_provider=(
                        cache_provider
                    ),
                    cache_read_latency_ms=(
                        cache_read_latency_ms
                    ),
                    cache_write_latency_ms=(
                        cache_write_latency_ms
                    ),
                    total_latency_ms=(
                        total_latency_ms
                    ),
                    citations=citations,
                    validation_errors=(
                        validation_errors
                    ),
                    prompt_tokens=prompt_tokens,
                    completion_tokens=(
                        completion_tokens
                    ),
                    total_tokens=total_tokens,
                )
            )

            self.db.commit()

            self.db.refresh(
                completed_run
            )

            return completed_run

        except Exception:
            self.db.rollback()
            raise
    def fail(
        self,
        *,
        rag_run: RAGRun,
        error: Exception,
        total_latency_ms: float,
        retrieval_latency_ms: (
            float | None
        ) = None,
        context_build_latency_ms: (
            float | None
        ) = None,
        prompt_build_latency_ms: (
            float | None
        ) = None,
        llm_latency_ms: (
            float | None
        ) = None,
        cache_enabled: bool = False,
        cache_hit: bool | None = None,
        cache_provider: str | None = None,
        cache_read_latency_ms: float | None = None,
        cache_write_latency_ms: float | None = None,
    ) -> None:
        self.db.rollback()

        managed_rag_run = (
            self.repository.get_by_id(
                rag_run_id=rag_run.id,
                user_id=rag_run.user_id,
            )
        )

        if managed_rag_run is None:
            return

        self.repository.fail_run(
            rag_run=managed_rag_run,
            error=error,
            total_latency_ms=(
                total_latency_ms
            ),
            retrieval_latency_ms=(
                retrieval_latency_ms
            ),
            context_build_latency_ms=(
                context_build_latency_ms
            ),
            prompt_build_latency_ms=(
                prompt_build_latency_ms
            ),
            llm_latency_ms=(
                llm_latency_ms
            ),
            cache_enabled=cache_enabled,
            cache_hit=cache_hit,
            cache_provider=cache_provider,
            cache_read_latency_ms=(
                cache_read_latency_ms
            ),
            cache_write_latency_ms=(
                cache_write_latency_ms
            ),
        )

        self.db.commit()