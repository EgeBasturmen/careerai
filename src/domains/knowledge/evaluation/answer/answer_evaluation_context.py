from dataclasses import dataclass

from src.domains.knowledge.rag.rag_context import (
    RAGContext,
)
from src.domains.knowledge.rag.rag_generation_result import (
    RAGGenerationResult,
)
from src.domains.knowledge.rag.rag_source_validator import (
    RAGSourceValidationResult,
)


@dataclass(frozen=True, slots=True)
class AnswerEvaluationContext:
    question: str

    generation_result: RAGGenerationResult

    rag_context: RAGContext

    source_validation_result: (
        RAGSourceValidationResult
    )

    @property
    def answer(
        self,
    ) -> str:
        return self.generation_result.answer

    @property
    def retrieved_context(
        self,
    ) -> str:
        return self.rag_context.text