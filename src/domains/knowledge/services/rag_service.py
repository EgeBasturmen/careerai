from time import perf_counter

from sqlalchemy.orm import Session
import logging
from src.domains.knowledge.rag.rag_context import (
    RAGContext,
)
from src.domains.knowledge.rag.rag_context_builder import (
    RAGContextBuilder,
)
from src.domains.knowledge.rag.rag_fallback_builder import (
    RAGFallbackBuilder,
)
from src.domains.knowledge.rag.rag_prompt_builder import (
    RAGPromptBuilder,
)
from src.domains.knowledge.rag.rag_response_parser import (
    RAGResponseParser,
)
from src.domains.knowledge.rag.rag_source_validator import (
    RAGSourceValidator,
)
from src.domains.knowledge.schemas.knowledge_retrieval_schema import (
    KnowledgeSearchRequest,
)
from src.domains.knowledge.schemas.rag_schema import (
    RAGAnswerResponse,
    RAGCitationResponse,
    RAGQuestionRequest,
    RAGSourceResponse,
)
from src.domains.knowledge.services.knowledge_retriever import (
    KnowledgeRetriever,
)
from src.domains.knowledge.services.rag_run_recorder import (
    RAGRunRecorder,
)
from src.infrastructure.llm.llm_factory import (
    get_llm_client,
)
from src.domains.knowledge.schemas.query_rewrite_schema import (
    QueryRewriteRequest,
    QueryRewriteResponse,
)

from src.domains.knowledge.services.query_rewriter import (
    QueryRewriter,
)

from src.infrastructure.queue.rag_evaluation_tasks import (
    evaluate_rag_answer_task,
)

logger = logging.getLogger(
    __name__
)

class RAGService:
    PROMPT_NAME = (
        RAGPromptBuilder.PROMPT_NAME
    )

    PROMPT_VERSION = (
        RAGPromptBuilder.PROMPT_VERSION
    )

    MAXIMUM_CONTEXT_CHARACTERS = 8000

    STATUS_SUCCESS = "SUCCESS"
    STATUS_NO_CONTEXT = "NO_CONTEXT"
    STATUS_INVALID_GENERATION = (
        "INVALID_GENERATION"
    )

    def __init__(
        self,
        db: Session,
    ):
        self.retriever = KnowledgeRetriever(
            db,
        )
        self.query_rewriter = (
            QueryRewriter()
        )
        self.context_builder = (
            RAGContextBuilder(
                maximum_context_characters=(
                    self.MAXIMUM_CONTEXT_CHARACTERS
                ),
            )
        )

        self.prompt_builder = (
            RAGPromptBuilder()
        )

        self.response_parser = (
            RAGResponseParser()
        )

        self.source_validator = (
            RAGSourceValidator()
        )

        self.fallback_builder = (
            RAGFallbackBuilder()
        )

        self.llm_client = (
            get_llm_client()
        )

        self.run_recorder = (
            RAGRunRecorder(
                db,
            )
        )

    def answer(
        self,
        request: RAGQuestionRequest,
        user_id: int,
    ) -> RAGAnswerResponse:
        total_started_at = perf_counter()

        normalized_question = (
            self._normalize_question(
                request.question,
            )
        )
        rewrite_response = (
            self.query_rewriter.rewrite(
                QueryRewriteRequest(
                    query=normalized_question,
                    category=request.category,
                    language=request.language,
                )
            )
        )
        rag_run = self.run_recorder.start(
            user_id=user_id,
            question=normalized_question,
            category=request.category,
            language=request.language,
            retrieval_limit=(
                request.retrieval_limit
            ),
            minimum_similarity=(
                request.minimum_similarity
            ),
            prompt_name=self.PROMPT_NAME,
            prompt_version=(
                self.PROMPT_VERSION
            ),
            llm_provider=(
                self._get_llm_provider_name()
            ),
            llm_model_name=(
                self._get_llm_model_name()
            ),
        )

        retrieval_latency_ms = 0.0
        context_build_latency_ms = 0.0
        prompt_build_latency_ms = 0.0
        llm_latency_ms = 0.0
        cache_enabled = False
        cache_hit: bool | None = None
        cache_provider: str | None = None

        cache_read_latency_ms: float | None = None
        cache_write_latency_ms: float | None = None

        try:
            retrieval_started_at = (
                perf_counter()
            )

            retrieval_execution = (
                self.retriever
                .retrieve_with_observability(
                    KnowledgeSearchRequest(
                        query=(
                            rewrite_response
                            .rewritten_query
                        ),
                        limit=(
                            request.retrieval_limit
                        ),
                        minimum_similarity=(
                            request.minimum_similarity
                        ),
                        category=request.category,
                        language=request.language,
                    )
                )
            )

            retrieval_response = (
                retrieval_execution.response
            )

            cache_enabled = (
                retrieval_execution.cache_enabled
            )

            cache_hit = (
                retrieval_execution.cache_hit
            )

            cache_provider = (
                retrieval_execution.cache_provider
            )

            cache_read_latency_ms = (
                retrieval_execution
                .cache_read_latency_ms
            )

            cache_write_latency_ms = (
                retrieval_execution
                .cache_write_latency_ms
            )

            retrieval_latency_ms = (
                perf_counter()
                - retrieval_started_at
            ) * 1000

            context_started_at = (
                perf_counter()
            )

            context = (
                self.context_builder.build(
                    retrieval_results=(
                        retrieval_response.results
                    ),
                )
            )

            context_build_latency_ms = (
                perf_counter()
                - context_started_at
            ) * 1000

            self.run_recorder.record_context_chunks(
                rag_run=rag_run,
                context=context,
            )

            sources = (
                self._build_source_responses(
                    context=context,
                )
            )

            if not context.items:
                return self._complete_no_context(
                    rag_run=rag_run,
                    question=normalized_question,
                    retrieval_response=(
                        retrieval_response
                    ),
                    retrieval_execution=(
                        retrieval_execution
                    ),
                    rewrite_response=(
                        rewrite_response
                    ),
                    context=context,
                    sources=sources,
                    total_started_at=(
                        total_started_at
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
                )

            prompt_started_at = (
                perf_counter()
            )

            prompt = (
                self.prompt_builder.build(
                    question=(
                        normalized_question
                    ),
                    context=context,
                )
            )

            prompt_build_latency_ms = (
                perf_counter()
                - prompt_started_at
            ) * 1000

            llm_started_at = (
                perf_counter()
            )

            raw_response = (
                self.llm_client.generate(
                    prompt=prompt,
                    prompt_name=(
                        self.PROMPT_NAME
                    ),
                    prompt_version=(
                        self.PROMPT_VERSION
                    ),
                )
            )

            llm_latency_ms = (
                perf_counter()
                - llm_started_at
            ) * 1000

            try:
                generation_result = (
                    self.response_parser.parse(
                        raw_response,
                    )
                )

            except ValueError as exc:
                return (
                    self
                    ._complete_invalid_generation(
                        rag_run=rag_run,
                        question=(
                            normalized_question
                        ),
                        retrieval_response=(
                            retrieval_response
                        ),
                        retrieval_execution=(
                            retrieval_execution
                        ),
                        rewrite_response=(
                            rewrite_response
                        ),
                        context=context,
                        sources=sources,
                        validation_errors=[
                            str(exc),
                        ],
                        total_started_at=(
                            total_started_at
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
                    )
                )

            validation_result = (
                self.source_validator.validate(
                    generation_result=(
                        generation_result
                    ),
                    context=context,
                )
            )

            if not validation_result.is_valid:
                return (
                    self
                    ._complete_invalid_generation(
                        rag_run=rag_run,
                        question=(
                            normalized_question
                        ),
                        retrieval_response=(
                            retrieval_response
                        ),
                        retrieval_execution=(
                            retrieval_execution
                        ),
                        rewrite_response=(
                            rewrite_response
                        ),
                        context=context,
                        sources=sources,
                        validation_errors=list(
                            validation_result
                            .validation_errors
                        ),
                        total_started_at=(
                            total_started_at
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
                    )
                )

            if (
                not generation_result
                .sufficient_context
            ):
                return self._complete_no_context(
                    rag_run=rag_run,
                    question=normalized_question,
                    retrieval_response=(
                        retrieval_response
                    ),
                    retrieval_execution=(
                        retrieval_execution
                    ),
                    rewrite_response=(
                        rewrite_response
                    ),
                    context=context,
                    sources=sources,
                    total_started_at=(
                        total_started_at
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
                    confidence=(
                        generation_result.confidence
                    ),
                )
            valid_source_numbers = set(
                validation_result
                .valid_source_numbers
            )

            citations = [
                RAGCitationResponse(
                    source_number=(
                        citation.source_number
                    ),
                    claim=citation.claim,
                )
                for citation in (
                    generation_result.citations
                )
                if citation.source_number
                in valid_source_numbers
            ]

            citation_payloads = [
                citation.model_dump()
                for citation in citations
            ]

            total_latency_ms = (
                perf_counter()
                - total_started_at
            ) * 1000

            completed_run = (
                self.run_recorder.complete(
                    rag_run=rag_run,
                    generation_status=(
                        self.STATUS_SUCCESS
                    ),
                    answer=(
                        generation_result.answer
                    ),
                    sufficient_context=True,
                    confidence=(
                        generation_result.confidence
                    ),
                    candidate_result_count=(
                        retrieval_response
                        .candidate_result_count
                    ),
                    retrieval_result_count=(
                        retrieval_response
                        .result_count
                    ),
                    retriever_name=(
                        retrieval_response
                        .retriever_name
                    ),
                    reranker_name=(
                        retrieval_response
                        .reranker_name
                    ),
                    reranker_model_name=(
                        retrieval_response
                        .reranker_model_name
                    ),
                    context=context,
                    embedding_provider=(
                        retrieval_response
                        .embedding_provider
                    ),
                    embedding_model_name=(
                        retrieval_response
                        .embedding_model_name
                    ),
                    original_query=(
                        rewrite_response.original_query
                    ),
                    rewritten_query=(
                        rewrite_response.rewritten_query
                    ),
                    was_rewritten=(
                        rewrite_response.was_rewritten
                    ),
                    rewrite_provider=(
                        rewrite_response.rewrite_provider
                    ),
                    rewrite_model_name=(
                        rewrite_response.rewrite_model_name
                    ),
                    rewrite_latency_ms=(
                        rewrite_response.rewrite_latency_ms
                    ),
                    rewrite_fallback_used=(
                        rewrite_response.fallback_used
                    ),
                    rewrite_fallback_reason=(
                        rewrite_response.fallback_reason
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
                    total_latency_ms=(
                        total_latency_ms
                    ),
                    cache_enabled=(
                        retrieval_execution.cache_enabled
                    ),
                    cache_hit=(
                        retrieval_execution.cache_hit
                    ),
                    cache_provider=(
                        retrieval_execution.cache_provider
                    ),
                    cache_read_latency_ms=(
                        retrieval_execution
                        .cache_read_latency_ms
                    ),
                    cache_write_latency_ms=(
                        retrieval_execution
                        .cache_write_latency_ms
                    ),
                    citations=(
                        citation_payloads
                    ),
                    validation_errors=[],
                )
            )

            self._enqueue_answer_evaluation(
                rag_run_id=completed_run.id,
            )

            return RAGAnswerResponse(
                question=(
                    normalized_question
                ),
                answer=(
                    generation_result.answer
                ),
                sufficient_context=True,
                confidence=(
                    generation_result.confidence
                ),
                generation_status=(
                    self.STATUS_SUCCESS
                ),
                candidate_result_count=(
                    retrieval_response
                    .candidate_result_count
                ),
                retrieval_result_count=(
                    retrieval_response
                    .result_count
                ),
                retriever_name=(
                    retrieval_response
                    .retriever_name
                ),
                reranker_name=(
                    retrieval_response
                    .reranker_name
                ),
                reranker_model_name=(
                    retrieval_response
                    .reranker_model_name
                ),
                original_query=(
                    rewrite_response.original_query
                ),
                rewritten_query=(
                    rewrite_response.rewritten_query
                ),
                was_rewritten=(
                    rewrite_response.was_rewritten
                ),
                rewrite_provider=(
                    rewrite_response.rewrite_provider
                ),
                rewrite_model_name=(
                    rewrite_response.rewrite_model_name
                ),
                rewrite_latency_ms=(
                    rewrite_response.rewrite_latency_ms
                ),
                rewrite_fallback_used=(
                    rewrite_response.fallback_used
                ),
                rewrite_fallback_reason=(
                    rewrite_response.fallback_reason
                ),
                context_source_count=(
                    context.source_count
                ),
                context_character_count=(
                    context.character_count
                ),
                embedding_provider=(
                    retrieval_response
                    .embedding_provider
                ),
                embedding_model_name=(
                    retrieval_response
                    .embedding_model_name
                ),
                citations=citations,
                sources=sources,
                validation_errors=[],
            )

        except Exception as exc:
            total_latency_ms = (
                perf_counter()
                - total_started_at
            ) * 1000

            self.run_recorder.fail(
                rag_run=rag_run,
                error=exc,
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
                cache_enabled=(
                    cache_enabled
                ),
                cache_hit=(
                    cache_hit
                ),
                cache_provider=(
                    cache_provider
                ),
                cache_read_latency_ms=(
                    cache_read_latency_ms
                ),
                cache_write_latency_ms=(
                    cache_write_latency_ms
                ),
            )

            raise

    def _complete_no_context(
        self,
        *,
        rag_run,
        question: str,
        rewrite_response: QueryRewriteResponse,
        retrieval_response,
        retrieval_execution,
        context: RAGContext,
        sources: list[RAGSourceResponse],
        total_started_at: float,
        retrieval_latency_ms: float,
        context_build_latency_ms: float,
        prompt_build_latency_ms: float,
        llm_latency_ms: float,
        confidence: float = 0.0,
    ) -> RAGAnswerResponse:
        answer = (
            self.fallback_builder
            .build_no_context_answer(
                question,
            )
        )

        total_latency_ms = (
            perf_counter()
            - total_started_at
        ) * 1000

        completed_run = (
            self.run_recorder.complete(
                rag_run=rag_run,
                generation_status=(
                    self.STATUS_NO_CONTEXT
                ),
                answer=answer,
                sufficient_context=False,
                confidence=confidence,
                candidate_result_count=(
                    retrieval_response
                    .candidate_result_count
                ),
                retrieval_result_count=(
                    retrieval_response
                    .result_count
                ),
                retriever_name=(
                    retrieval_response
                    .retriever_name
                ),
                reranker_name=(
                    retrieval_response
                    .reranker_name
                ),
                reranker_model_name=(
                    retrieval_response
                    .reranker_model_name
                ),
                original_query=(
                    rewrite_response
                    .original_query
                ),
                rewritten_query=(
                    rewrite_response
                    .rewritten_query
                ),
                was_rewritten=(
                    rewrite_response
                    .was_rewritten
                ),
                rewrite_provider=(
                    rewrite_response
                    .rewrite_provider
                ),
                rewrite_model_name=(
                    rewrite_response
                    .rewrite_model_name
                ),
                rewrite_latency_ms=(
                    rewrite_response
                    .rewrite_latency_ms
                ),
                rewrite_fallback_used=(
                    rewrite_response
                    .fallback_used
                ),
                rewrite_fallback_reason=(
                    rewrite_response
                    .fallback_reason
                ),
                context=context,
                embedding_provider=(
                    retrieval_response
                    .embedding_provider
                ),
                embedding_model_name=(
                    retrieval_response
                    .embedding_model_name
                ),
                retrieval_latency_ms=(
                    retrieval_latency_ms
                ),
                cache_enabled=(
                    retrieval_execution
                    .cache_enabled
                ),
                cache_hit=(
                    retrieval_execution
                    .cache_hit
                ),
                cache_provider=(
                    retrieval_execution
                    .cache_provider
                ),
                cache_read_latency_ms=(
                    retrieval_execution
                    .cache_read_latency_ms
                ),
                cache_write_latency_ms=(
                    retrieval_execution
                    .cache_write_latency_ms
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
                total_latency_ms=(
                    total_latency_ms
                ),
                citations=[],
                validation_errors=[],
            )
        )

        return RAGAnswerResponse(
            question=question,
            answer=answer,
            sufficient_context=False,
            confidence=confidence,
            generation_status=(
                self.STATUS_NO_CONTEXT
            ),
            candidate_result_count=(
                retrieval_response
                .candidate_result_count
            ),
            retrieval_result_count=(
                retrieval_response
                .result_count
            ),
            retriever_name=(
                retrieval_response
                .retriever_name
            ),
            reranker_name=(
                retrieval_response
                .reranker_name
            ),
            reranker_model_name=(
                retrieval_response
                .reranker_model_name
            ),
            original_query=(
                rewrite_response.original_query
            ),
            rewritten_query=(
                rewrite_response.rewritten_query
            ),
            was_rewritten=(
                rewrite_response.was_rewritten
            ),
            rewrite_provider=(
                rewrite_response.rewrite_provider
            ),
            rewrite_model_name=(
                rewrite_response.rewrite_model_name
            ),
            rewrite_latency_ms=(
                rewrite_response.rewrite_latency_ms
            ),
            rewrite_fallback_used=(
                rewrite_response.fallback_used
            ),
            rewrite_fallback_reason=(
                rewrite_response.fallback_reason
            ),
            context_source_count=(
                context.source_count
            ),
            context_character_count=(
                context.character_count
            ),
            embedding_provider=(
                retrieval_response
                .embedding_provider
            ),
            embedding_model_name=(
                retrieval_response
                .embedding_model_name
            ),
            citations=[],
            sources=sources,
            validation_errors=[],
        )

    def _complete_invalid_generation(
        self,
        *,
        rag_run,
        question: str,
        retrieval_response,
        retrieval_execution,
        rewrite_response: QueryRewriteResponse,
        context: RAGContext,
        sources: list[
            RAGSourceResponse
        ],
        validation_errors: list[str],
        total_started_at: float,
        retrieval_latency_ms: float,
        context_build_latency_ms: float,
        prompt_build_latency_ms: float,
        llm_latency_ms: float,
        
    ) -> RAGAnswerResponse:
        answer = (
            self.fallback_builder
            .build_invalid_generation_answer(
                question,
            )
        )

        total_latency_ms = (
            perf_counter()
            - total_started_at
        ) * 1000

        self.run_recorder.complete(
            rag_run=rag_run,
            generation_status=(
                self.STATUS_INVALID_GENERATION
            ),
            answer=answer,
            sufficient_context=False,
            confidence=0.0,
            candidate_result_count=(
                retrieval_response
                .candidate_result_count
            ),
            retrieval_result_count=(
                retrieval_response
                .result_count
            ),
            retriever_name=(
                retrieval_response
                .retriever_name
            ),
            reranker_name=(
                retrieval_response
                .reranker_name
            ),
            reranker_model_name=(
                retrieval_response
                .reranker_model_name
            ),
            context=context,
            embedding_provider=(
                retrieval_response
                .embedding_provider
            ),
            embedding_model_name=(
                retrieval_response
                .embedding_model_name
            ),
            original_query=(
                rewrite_response.original_query
            ),
            rewritten_query=(
                rewrite_response.rewritten_query
            ),
            was_rewritten=(
                rewrite_response.was_rewritten
            ),
            rewrite_provider=(
                rewrite_response.rewrite_provider
            ),
            rewrite_model_name=(
                rewrite_response.rewrite_model_name
            ),
            rewrite_latency_ms=(
                rewrite_response.rewrite_latency_ms
            ),
            rewrite_fallback_used=(
                rewrite_response.fallback_used
            ),
            rewrite_fallback_reason=(
                rewrite_response.fallback_reason
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
            total_latency_ms=(
                total_latency_ms
            ),
            cache_enabled=(
                retrieval_execution.cache_enabled
            ),
            cache_hit=(
                retrieval_execution.cache_hit
            ),
            cache_provider=(
                retrieval_execution.cache_provider
            ),
            cache_read_latency_ms=(
                retrieval_execution
                .cache_read_latency_ms
            ),
            cache_write_latency_ms=(
                retrieval_execution
                .cache_write_latency_ms
            ),
            citations=[],
            validation_errors=(
                validation_errors
            ),
        )



        return RAGAnswerResponse(
            question=question,
            answer=answer,
            sufficient_context=False,
            confidence=0.0,
            generation_status=(
                self.STATUS_INVALID_GENERATION
            ),
            candidate_result_count=(
                retrieval_response
                .candidate_result_count
            ),
            retrieval_result_count=(
                retrieval_response
                .result_count
            ),
            retriever_name=(
                retrieval_response
                .retriever_name
            ),
            reranker_name=(
                retrieval_response
                .reranker_name
            ),
            reranker_model_name=(
                retrieval_response
                .reranker_model_name
            ),

            original_query=(
                rewrite_response.original_query
            ),
            rewritten_query=(
                rewrite_response.rewritten_query
            ),
            was_rewritten=(
                rewrite_response.was_rewritten
            ),
            rewrite_provider=(
                rewrite_response.rewrite_provider
            ),
            rewrite_model_name=(
                rewrite_response.rewrite_model_name
            ),
            rewrite_latency_ms=(
                rewrite_response.rewrite_latency_ms
            ),
            rewrite_fallback_used=(
                rewrite_response.fallback_used
            ),
            rewrite_fallback_reason=(
                rewrite_response.fallback_reason
            ),
            context_source_count=(
                context.source_count
            ),
            context_character_count=(
                context.character_count
            ),
            embedding_provider=(
                retrieval_response
                .embedding_provider
            ),
            embedding_model_name=(
                retrieval_response
                .embedding_model_name
            ),
            citations=[],
            sources=sources,
            validation_errors=(
                validation_errors
            ),
        )

    def _build_source_responses(
        self,
        context: RAGContext,
    ) -> list[RAGSourceResponse]:
        return [
            RAGSourceResponse(
                source_number=(
                    item.source_number
                ),
                chunk_id=item.chunk_id,
                document_id=(
                    item.document_id
                ),
                document_title=(
                    item.document_title
                ),
                similarity_score=(
                    item.similarity_score
                ),
                source_type=(
                    item.source_type
                ),
                source_uri=(
                    item.source_uri
                ),
                category=item.category,
                language=item.language,
            )
            for item in context.items
        ]

    def _normalize_question(
        self,
        question: str,
    ) -> str:
        normalized_question = " ".join(
            question
            .strip()
            .split()
        )

        if not normalized_question:
            raise ValueError(
                "RAG question cannot be empty"
            )

        return normalized_question

    def _get_llm_provider_name(
        self,
    ) -> str | None:
        provider_name = getattr(
            self.llm_client,
            "provider_name",
            None,
        )

        if provider_name:
            return str(
                provider_name
            )

        return (
            self.llm_client
            .__class__
            .__name__
        )

    def _get_llm_model_name(
        self,
    ) -> str | None:
        model_name = getattr(
            self.llm_client,
            "model_name",
            None,
        )

        if model_name is None:
            return None

        return str(
            model_name
        )

    def _enqueue_answer_evaluation(
        self,
        *,
        rag_run_id: int,
    ) -> None:
        try:
            evaluate_rag_answer_task.delay(
                rag_run_id,
            )

        except Exception:
            logger.exception(
                "Could not enqueue RAG answer "
                "evaluation task for "
                "rag_run_id=%s",
                rag_run_id,
            )