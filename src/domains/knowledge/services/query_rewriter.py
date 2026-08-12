from time import perf_counter

from src.domains.knowledge.rag.query_rewrite_prompt_builder import (
    QueryRewritePromptBuilder,
)
from src.domains.knowledge.rag.query_rewrite_response_parser import (
    QueryRewriteResponseParser,
)
from src.domains.knowledge.schemas.query_rewrite_schema import (
    QueryRewriteRequest,
    QueryRewriteResponse,
)
from src.infrastructure.llm.llm_factory import (
    get_llm_client,
)


class QueryRewriter:
    def __init__(
        self,
    ):
        self.llm_client = (
            get_llm_client()
        )

        self.prompt_builder = (
            QueryRewritePromptBuilder()
        )

        self.response_parser = (
            QueryRewriteResponseParser()
        )

    def rewrite(
        self,
        request: QueryRewriteRequest,
    ) -> QueryRewriteResponse:
        original_query = (
            self._normalize_query(
                request.query
            )
        )

        started_at = perf_counter()

        try:
            prompt = (
                self.prompt_builder.build(
                    query=original_query,
                    category=(
                        request.category
                    ),
                    language=(
                        request.language
                    ),
                )
            )

            raw_response = (
                self.llm_client.generate(
                    prompt=prompt,
                    prompt_name=(
                        self.prompt_builder
                        .PROMPT_NAME
                    ),
                    prompt_version=(
                        self.prompt_builder
                        .PROMPT_VERSION
                    ),
                )
            )

            rewritten_query = (
                self.response_parser.parse(
                    raw_response
                )
            )

            rewrite_latency_ms = (
                perf_counter()
                - started_at
            ) * 1000

            return QueryRewriteResponse(
                original_query=(
                    original_query
                ),
                rewritten_query=(
                    rewritten_query
                ),
                was_rewritten=(
                    rewritten_query
                    != original_query
                ),
                rewrite_provider=(
                    self._get_llm_provider_name()
                ),
                rewrite_model_name=(
                    self._get_llm_model_name()
                ),
                rewrite_latency_ms=(
                    rewrite_latency_ms
                ),
                fallback_used=False,
                fallback_reason=None,
            )

        except Exception as exc:
            rewrite_latency_ms = (
                perf_counter()
                - started_at
            ) * 1000

            return QueryRewriteResponse(
                original_query=(
                    original_query
                ),
                rewritten_query=(
                    original_query
                ),
                was_rewritten=False,
                rewrite_provider=(
                    self._get_llm_provider_name()
                ),
                rewrite_model_name=(
                    self._get_llm_model_name()
                ),
                rewrite_latency_ms=(
                    rewrite_latency_ms
                ),
                fallback_used=True,
                fallback_reason=(
                    self._build_fallback_reason(
                        exc
                    )
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
                "Query rewrite input "
                "cannot be empty"
            )

        return normalized_query

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

    def _build_fallback_reason(
        self,
        error: Exception,
    ) -> str:
        return (
            f"{type(error).__name__}: "
            f"{str(error)}"
        )[:1000]