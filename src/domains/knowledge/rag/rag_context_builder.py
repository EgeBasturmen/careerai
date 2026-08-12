from src.domains.knowledge.rag.rag_context import (
    RAGContext,
    RAGContextItem,
)
from src.domains.knowledge.schemas.knowledge_retrieval_schema import (
    KnowledgeRetrievalResult,
)


class RAGContextBuilder:
    TRUNCATION_SUFFIX = "..."
    MINIMUM_TRUNCATED_CONTENT_CHARACTERS = 100

    def __init__(
        self,
        maximum_context_characters: int = 8000,
    ):
        if maximum_context_characters <= 0:
            raise ValueError(
                "maximum_context_characters "
                "must be greater than zero"
            )

        self.maximum_context_characters = (
            maximum_context_characters
        )

    def build(
        self,
        retrieval_results: list[
            KnowledgeRetrievalResult
        ],
    ) -> RAGContext:
        if not retrieval_results:
            return RAGContext(
                text="",
                items=(),
                source_count=0,
                character_count=0,
            )

        context_parts: list[str] = []
        context_items: list[RAGContextItem] = []

        for result in retrieval_results:
            source_number = (
                len(context_items) + 1
            )

            source_text = self._build_source_text(
                source_number=source_number,
                result=result,
            )

            current_context_text = (
                "\n\n".join(context_parts)
            )

            separator_length = (
                2
                if context_parts
                else 0
            )

            projected_character_count = (
                len(current_context_text)
                + separator_length
                + len(source_text)
            )

            if (
                projected_character_count
                > self.maximum_context_characters
            ):
                remaining_characters = (
                    self.maximum_context_characters
                    - len(current_context_text)
                    - separator_length
                )

                truncated_result = (
                    self._truncate_result_to_fit(
                        source_number=source_number,
                        result=result,
                        available_characters=(
                            remaining_characters
                        ),
                    )
                )

                if truncated_result is None:
                    break

                result = truncated_result

                source_text = self._build_source_text(
                    source_number=source_number,
                    result=result,
                )

            context_parts.append(
                source_text
            )

            context_items.append(
                self._build_context_item(
                    source_number=source_number,
                    result=result,
                )
            )

            context_text = "\n\n".join(
                context_parts
            )

            if (
                len(context_text)
                >= self.maximum_context_characters
            ):
                break

        context_text = "\n\n".join(
            context_parts
        )

        return RAGContext(
            text=context_text,
            items=tuple(
                context_items
            ),
            source_count=len(
                context_items
            ),
            character_count=len(
                context_text
            ),
        )

    def _truncate_result_to_fit(
        self,
        *,
        source_number: int,
        result: KnowledgeRetrievalResult,
        available_characters: int,
    ) -> KnowledgeRetrievalResult | None:
        empty_content_result = result.model_copy(
            update={
                "content": "",
            }
        )

        source_overhead = len(
            self._build_source_text(
                source_number=source_number,
                result=empty_content_result,
            )
        )

        available_content_characters = (
            available_characters
            - source_overhead
            - len(self.TRUNCATION_SUFFIX)
        )

        if (
            available_content_characters
            < self.MINIMUM_TRUNCATED_CONTENT_CHARACTERS
        ):
            return None

        truncated_content = (
            result.content[
                :available_content_characters
            ]
            .rstrip()
        )

        if not truncated_content:
            return None

        return result.model_copy(
            update={
                "content": (
                    truncated_content
                    + self.TRUNCATION_SUFFIX
                )
            }
        )

    def _build_context_item(
        self,
        *,
        source_number: int,
        result: KnowledgeRetrievalResult,
    ) -> RAGContextItem:
        return RAGContextItem(
            source_number=source_number,
            chunk_id=result.chunk_id,
            document_id=result.document_id,
            chunk_index=result.chunk_index,
            document_title=(
                result.document_title
            ),
            content=result.content,
            similarity_score=(
                result.similarity_score
            ),
            source_type=result.source_type,
            source_uri=result.source_uri,
            category=result.category,
            language=result.language,
        )

    def _build_source_text(
        self,
        *,
        source_number: int,
        result: KnowledgeRetrievalResult,
    ) -> str:
        source_lines = [
            f"[Source {source_number}]",
            (
                "Title: "
                f"{result.document_title}"
            ),
            (
                "Category: "
                f"{result.category or 'unknown'}"
            ),
            (
                "Language: "
                f"{result.language}"
            ),
        ]

        if result.source_uri:
            source_lines.append(
                (
                    "Source URI: "
                    f"{result.source_uri}"
                )
            )

        source_lines.extend(
            [
                (
                    "Relevance Score: "
                    f"{result.similarity_score:.4f}"
                ),
                "Content:",
                result.content.strip(),
            ]
        )

        return "\n".join(
            source_lines
        )