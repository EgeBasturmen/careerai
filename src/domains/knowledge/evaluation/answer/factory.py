from src.domains.knowledge.evaluation.answer.answer_relevance_evaluator import (
    AnswerRelevanceEvaluator,
)
from src.domains.knowledge.evaluation.answer.citation_coverage_evaluator import (
    CitationCoverageEvaluator,
)
from src.domains.knowledge.evaluation.answer.faithfulness_evaluator import (
    FaithfulnessEvaluator,
)
from src.domains.knowledge.evaluation.answer.rag_answer_evaluator import (
    RAGAnswerEvaluator,
)
from src.domains.knowledge.services.answer_evaluation_service import (
    AnswerEvaluationService,
)
from src.infrastructure.llm.base import (
    LLMClient,
)


def create_rag_answer_evaluator(
    *,
    llm_client: LLMClient,
) -> RAGAnswerEvaluator:
    return RAGAnswerEvaluator(
        evaluators=(
            FaithfulnessEvaluator(
                llm_client=llm_client,
            ),
            AnswerRelevanceEvaluator(
                llm_client=llm_client,
            ),
            CitationCoverageEvaluator(),
        ),
    )


def create_answer_evaluation_service(
    *,
    llm_client: LLMClient,
) -> AnswerEvaluationService:
    answer_evaluator = (
        create_rag_answer_evaluator(
            llm_client=llm_client,
        )
    )

    return AnswerEvaluationService(
        answer_evaluator=answer_evaluator,
    )