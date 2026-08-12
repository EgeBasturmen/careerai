from src.domains.knowledge.evaluation.answer.answer_evaluation_context import (
    AnswerEvaluationContext,
)
from src.domains.knowledge.evaluation.answer.answer_evaluation_result import (
    AnswerEvaluationResult,
)
from src.domains.knowledge.evaluation.answer.base_answer_evaluator import (
    BaseAnswerEvaluator,
)


class CitationCoverageEvaluator(
    BaseAnswerEvaluator,
):
    def __init__(
        self,
        pass_threshold: float = 1.0,
    ) -> None:
        if not 0.0 <= pass_threshold <= 1.0:
            raise ValueError(
                "Pass threshold must be "
                "between 0.0 and 1.0"
            )

        self.pass_threshold = pass_threshold

    @property
    def evaluator_name(
        self,
    ) -> str:
        return "citation_coverage"

    def evaluate(
        self,
        *,
        evaluation_context: (
            AnswerEvaluationContext
        ),
    ) -> AnswerEvaluationResult:
        citations = self._get_unique_numbers(
            evaluation_context
            .generation_result
            .citations
        )

        valid_source_numbers = (
            self._get_unique_numbers(
                evaluation_context
                .source_validation_result
                .valid_source_numbers
            )
        )

        invalid_source_numbers = (
            self._get_unique_numbers(
                evaluation_context
                .source_validation_result
                .invalid_source_numbers
            )
        )

        if not citations:
            return self._evaluate_without_citations(
                evaluation_context=(
                    evaluation_context
                ),
            )

        valid_citation_count = len(
            citations.intersection(
                valid_source_numbers,
            )
        )

        score = (
            valid_citation_count
            / len(citations)
        )

        passed = (
            score >= self.pass_threshold
        )

        explanation = self._build_explanation(
            citation_count=len(citations),
            valid_citation_count=(
                valid_citation_count
            ),
            invalid_source_numbers=(
                invalid_source_numbers
            ),
        )

        return AnswerEvaluationResult(
            evaluator_name=self.evaluator_name,
            score=score,
            passed=passed,
            explanation=explanation,
        )

    def _evaluate_without_citations(
        self,
        *,
        evaluation_context: (
            AnswerEvaluationContext
        ),
    ) -> AnswerEvaluationResult:
        sufficient_context = (
            evaluation_context
            .generation_result
            .sufficient_context
        )

        if not sufficient_context:
            return AnswerEvaluationResult(
                evaluator_name=(
                    self.evaluator_name
                ),
                score=1.0,
                passed=True,
                explanation=(
                    "The model reported insufficient "
                    "context and did not provide "
                    "citations."
                ),
            )

        return AnswerEvaluationResult(
            evaluator_name=self.evaluator_name,
            score=0.0,
            passed=False,
            explanation=(
                "The model reported sufficient "
                "context but did not provide "
                "any citations."
            ),
        )

    def _build_explanation(
        self,
        *,
        citation_count: int,
        valid_citation_count: int,
        invalid_source_numbers: set[int],
    ) -> str:
        if valid_citation_count == citation_count:
            return (
                f"All {citation_count} cited source "
                "numbers are valid."
            )

        invalid_numbers = ", ".join(
            str(source_number)
            for source_number in sorted(
                invalid_source_numbers
            )
        )

        if not invalid_numbers:
            invalid_numbers = "unknown"

        return (
            f"{valid_citation_count} of "
            f"{citation_count} cited source "
            "numbers are valid. Invalid source "
            f"numbers: {invalid_numbers}."
        )

    def _get_unique_numbers(
        self,
        values: tuple[int, ...] | list[int],
    ) -> set[int]:
        return set(values)