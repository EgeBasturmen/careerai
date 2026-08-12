from unittest.mock import Mock

import pytest

from src.domains.knowledge.evaluation.answer.answer_evaluation_context import (
    AnswerEvaluationContext,
)
from src.domains.knowledge.evaluation.answer.faithfulness_evaluator import (
    FaithfulnessEvaluator,
)
from src.domains.knowledge.rag.rag_context import (
    RAGContext,
)
from src.domains.knowledge.rag.rag_generation_result import (
    RAGGenerationResult,
)
from src.domains.knowledge.rag.rag_source_validator import (
    RAGSourceValidationResult,
)
from src.infrastructure.llm.base import (
    LLMClient,
)

def build_evaluation_context(
    *,
    question: str = "What is FastAPI?",
    answer: str = (
        "FastAPI is a Python web framework."
    ),
    retrieved_context: str = (
        "[Source 1]\n"
        "FastAPI is a modern Python "
        "web framework."
    ),
) -> AnswerEvaluationContext:
    return AnswerEvaluationContext(
        question=question,
        generation_result=(
            RAGGenerationResult(
                answer=answer,
                citations=(),
                sufficient_context=True,
                confidence=0.9,
                raw_response="{}",
            )
        ),
        rag_context=RAGContext(
            text=retrieved_context,
            items=(),
            source_count=0,
            character_count=len(
                retrieved_context
            ),
        ),
        source_validation_result=(
            RAGSourceValidationResult(
                is_valid=True,
                valid_source_numbers=(),
                invalid_source_numbers=(),
                validation_errors=(),
            )
        ),
    )