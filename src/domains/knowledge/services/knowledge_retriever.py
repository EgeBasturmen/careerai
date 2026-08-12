from sqlalchemy.orm import Session

from src.core.config.settings import settings
from src.domains.embeddings.clients.factory import (
    get_embedding_client,
)
from src.domains.knowledge.cache.base_retrieval_cache import (
    RetrievalCache,
)
from src.domains.knowledge.cache.retrieval_cache_factory import (
    get_retrieval_cache,
)
from src.domains.knowledge.cache.retrieval_cache_key_builder import (
    RetrievalCacheKeyBuilder,
)
from src.domains.knowledge.rerankers.factory import (
    get_knowledge_reranker,
)
from src.domains.knowledge.retrievers.factory import (
    get_knowledge_retriever,
)
from src.domains.knowledge.schemas.knowledge_retrieval_schema import (
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
)
from time import perf_counter

from src.domains.knowledge.schemas.knowledge_retrieval_execution_schema import (
    KnowledgeRetrievalExecution,
)

class KnowledgeRetriever:
    def __init__(
        self,
        db: Session,
        retrieval_cache: (
            RetrievalCache | None
        ) = None,
        cache_key_builder: (
            RetrievalCacheKeyBuilder | None
        ) = None,
    ) -> None:
        self.embedding_client = (
            get_embedding_client()
        )

        self.retriever = (
            get_knowledge_retriever(
                db=db,
                retriever_name=(
                    settings
                    .knowledge_retriever_name
                ),
                embedding_model_name=(
                    self.embedding_client
                    .model_name
                ),
            )
        )

        self.reranker = (
            get_knowledge_reranker()
        )

        self.cache_key_builder = (
            cache_key_builder
            or RetrievalCacheKeyBuilder()
        )

        if (
            settings
            .knowledge_retrieval_cache_enabled
        ):
            self.retrieval_cache = (
                retrieval_cache
                or get_retrieval_cache()
            )
        else:
            self.retrieval_cache = None

    def retrieve(
        self,
        request: KnowledgeSearchRequest,
    ) -> KnowledgeSearchResponse:
        execution = (
            self.retrieve_with_observability(
                request
            )
        )

        return execution.response
    
    def retrieve_with_observability(
        self,
        request: KnowledgeSearchRequest,
    ) -> KnowledgeRetrievalExecution:
        normalized_query = (
            self._normalize_query(
                request.query
            )
        )

        normalized_request = (
            request.model_copy(
                update={
                    "query": normalized_query,
                }
            )
        )

        cache_enabled = (
            self.retrieval_cache
            is not None
        )

        cache_provider = (
            self.retrieval_cache
            .provider_name
            if self.retrieval_cache
            is not None
            else None
        )

        cache_key = (
            self._build_cache_key(
                normalized_request
            )
        )

        cache_read_latency_ms: (
            float | None
        ) = None

        cache_write_latency_ms: (
            float | None
        ) = None

        cache_hit: bool | None = None

        if (
            cache_key is not None
            and self.retrieval_cache
            is not None
        ):
            cache_read_started_at = (
                perf_counter()
            )

            cached_response = (
                self._get_cached_response(
                    cache_key
                )
            )

            cache_read_latency_ms = (
                perf_counter()
                - cache_read_started_at
            ) * 1000

            cache_hit = (
                cached_response
                is not None
            )

            if cached_response is not None:
                return (
                    KnowledgeRetrievalExecution(
                        response=(
                            cached_response
                        ),
                        cache_enabled=True,
                        cache_hit=True,
                        cache_provider=(
                            cache_provider
                        ),
                        cache_read_latency_ms=(
                            cache_read_latency_ms
                        ),
                        cache_write_latency_ms=None,
                    )
                )

        response = (
            self._retrieve_uncached(
                normalized_request
            )
        )

        if (
            cache_key is not None
            and self.retrieval_cache
            is not None
        ):
            cache_write_started_at = (
                perf_counter()
            )

            self._cache_response(
                key=cache_key,
                response=response,
            )

            cache_write_latency_ms = (
                perf_counter()
                - cache_write_started_at
            ) * 1000

        return KnowledgeRetrievalExecution(
            response=response,
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

    def _retrieve_uncached(
        self,
        request: KnowledgeSearchRequest,
    ) -> KnowledgeSearchResponse:
        query_embedding = (
            self.embedding_client.embed_text(
                request.query
            )
        )

        candidate_limit = request.limit

        if self.reranker is not None:
            candidate_limit = max(
                request.limit
                * settings
                .knowledge_reranker_candidate_multiplier,
                request.limit,
            )

        retrieved_results = (
            self.retriever.retrieve(
                query_text=request.query,
                query_embedding=(
                    query_embedding
                ),
                limit=candidate_limit,
                minimum_similarity=(
                    request
                    .minimum_similarity
                ),
                category=request.category,
                language=request.language,
            )
        )

        candidate_result_count = len(
            retrieved_results
        )

        if self.reranker is None:
            results = retrieved_results[
                : request.limit
            ]
        else:
            results = (
                self.reranker.rerank(
                    query_text=request.query,
                    results=(
                        retrieved_results
                    ),
                    limit=request.limit,
                    minimum_score=(
                        settings
                        .knowledge_reranker_minimum_score
                    ),
                )
            )

        return KnowledgeSearchResponse(
            query=request.query,
            embedding_provider=(
                self.embedding_client
                .provider_name
            ),
            embedding_model_name=(
                self.embedding_client
                .model_name
            ),
            retriever_name=(
                self.retriever
                .retriever_name
            ),
            reranker_name=(
                self.reranker
                .reranker_name
                if self.reranker
                is not None
                else None
            ),
            reranker_model_name=(
                settings
                .knowledge_reranker_model_name
                if self.reranker
                is not None
                else None
            ),
            candidate_result_count=(
                candidate_result_count
            ),
            result_count=len(
                results
            ),
            minimum_similarity=(
                request
                .minimum_similarity
            ),
            category=request.category,
            language=request.language,
            results=results,
        )

    def _build_cache_key(
        self,
        request: KnowledgeSearchRequest,
    ) -> str | None:
        if self.retrieval_cache is None:
            return None

        return self.cache_key_builder.build(
            request
        )

    def _get_cached_response(
        self,
        key: str | None,
    ) -> KnowledgeSearchResponse | None:
        if (
            key is None
            or self.retrieval_cache is None
        ):
            return None

        return self.retrieval_cache.get(
            key
        )

    def _cache_response(
        self,
        key: str | None,
        response: KnowledgeSearchResponse,
    ) -> None:
        if (
            key is None
            or self.retrieval_cache is None
        ):
            return

        self.retrieval_cache.set(
            key=key,
            value=response,
            ttl_seconds=(
                settings
                .knowledge_retrieval_cache_ttl_seconds
            ),
        )

    def _normalize_query(
        self,
        query: str,
    ) -> str:
        normalized_query = " ".join(
            query
            .strip()
            .split()
        )

        if not normalized_query:
            raise ValueError(
                "Knowledge search query "
                "cannot be empty"
            )

        return normalized_query