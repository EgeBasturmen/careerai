import json

from pydantic import ValidationError

from src.domains.knowledge.rag.rag_generation_result import (
    RAGGeneratedCitation,
    RAGGenerationResult,
)
from src.domains.knowledge.schemas.rag_generation_schema import (
    RAGGeneratedAnswerSchema,
)


class RAGResponseParser:
    def parse(
        self,
        raw_response: str,
    ) -> RAGGenerationResult:
        normalized_response = (
            self._normalize_response(
                raw_response,
            )
        )

        try:
            payload = json.loads(
                normalized_response
            )

            validated = (
                RAGGeneratedAnswerSchema
                .model_validate(
                    payload
                )
            )

        except (
            json.JSONDecodeError,
            ValidationError,
            TypeError,
        ) as exc:
            raise ValueError(
                "LLM returned an invalid "
                "structured RAG response"
            ) from exc

        citations = tuple(
            RAGGeneratedCitation(
                source_number=(
                    citation.source_number
                ),
                claim=citation.claim.strip(),
            )
            for citation in validated.citations
        )

        return RAGGenerationResult(
            answer=validated.answer.strip(),
            citations=citations,
            sufficient_context=(
                validated.sufficient_context
            ),
            confidence=(
                validated.confidence
            ),
            raw_response=raw_response,
        )

    def _normalize_response(
        self,
        raw_response: str,
    ) -> str:
        response = raw_response.strip()

        if response.startswith("```json"):
            response = response[
                len("```json"):
            ]

        elif response.startswith("```"):
            response = response[
                len("```"):
            ]

        if response.endswith("```"):
            response = response[
                :-len("```")
            ]

        return response.strip()