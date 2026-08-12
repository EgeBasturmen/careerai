from dataclasses import dataclass

from src.domains.knowledge.rag.rag_context import (
    RAGContext,
)
from src.domains.knowledge.rag.rag_generation_result import (
    RAGGenerationResult,
)


@dataclass(frozen=True, slots=True)
class RAGSourceValidationResult:
    is_valid: bool

    valid_source_numbers: tuple[
        int,
        ...
    ]

    invalid_source_numbers: tuple[
        int,
        ...
    ]

    validation_errors: tuple[
        str,
        ...
    ]


class RAGSourceValidator:
    def validate(
        self,
        generation_result: RAGGenerationResult,
        context: RAGContext,
    ) -> RAGSourceValidationResult:
        available_source_numbers = {
            item.source_number
            for item in context.items
        }

        cited_source_numbers = {
            citation.source_number
            for citation in (
                generation_result.citations
            )
        }

        valid_source_numbers = (
            cited_source_numbers
            & available_source_numbers
        )

        invalid_source_numbers = (
            cited_source_numbers
            - available_source_numbers
        )

        validation_errors: list[str] = []

        if invalid_source_numbers:
            validation_errors.append(
                "The generated answer cited "
                "unavailable sources: "
                + ", ".join(
                    str(source_number)
                    for source_number in sorted(
                        invalid_source_numbers
                    )
                )
            )

        if (
            generation_result
            .sufficient_context
            and not context.items
        ):
            validation_errors.append(
                "The model marked the context "
                "as sufficient although no "
                "sources were retrieved"
            )

        if (
            generation_result
            .sufficient_context
            and not valid_source_numbers
        ):
            validation_errors.append(
                "The model produced a grounded "
                "answer without valid citations"
            )

        return RAGSourceValidationResult(
            is_valid=(
                not validation_errors
            ),
            valid_source_numbers=tuple(
                sorted(
                    valid_source_numbers
                )
            ),
            invalid_source_numbers=tuple(
                sorted(
                    invalid_source_numbers
                )
            ),
            validation_errors=tuple(
                validation_errors
            ),
        )