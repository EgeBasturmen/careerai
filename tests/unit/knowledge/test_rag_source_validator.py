from src.domains.knowledge.rag.rag_context import (
    RAGContext,
    RAGContextItem,
)
from src.domains.knowledge.rag.rag_generation_result import (
    RAGGeneratedCitation,
    RAGGenerationResult,
)
from src.domains.knowledge.rag.rag_source_validator import (
    RAGSourceValidator,
)


def test_rejects_unknown_source_number() -> None:
    context = RAGContext(
        text="Example context",
        items=(
            RAGContextItem(
                source_number=1,
                chunk_id=10,
                chunk_index=0,
                document_id=20,
                document_title="Test",
                content="Test content",
                similarity_score=0.9,
                source_type="manual",
                source_uri=None,
                category="test",
                language="en",
            ),
        ),
        source_count=1,
        character_count=15,
    )

    generation_result = RAGGenerationResult(
        answer="Generated answer",
        citations=(
            RAGGeneratedCitation(
                source_number=7,
                claim="Unsupported claim",
            ),
        ),
        sufficient_context=True,
        confidence=0.9,
        raw_response="{}",
    )

    validator = RAGSourceValidator()

    result = validator.validate(
        generation_result=(
            generation_result
        ),
        context=context,
    )

    assert result.is_valid is False
    assert result.invalid_source_numbers == (
        7,
    )