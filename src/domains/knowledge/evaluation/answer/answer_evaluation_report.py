from dataclasses import dataclass
from statistics import mean

from src.domains.knowledge.evaluation.answer.answer_evaluation_result import (
    AnswerEvaluationResult,
)


@dataclass(frozen=True, slots=True)
class AnswerEvaluationReport:
    results: tuple[
        AnswerEvaluationResult,
        ...,
    ]

    @property
    def overall_score(
        self,
    ) -> float:
        if not self.results:
            return 0.0

        return mean(
            result.score
            for result in self.results
        )

    @property
    def passed(
        self,
    ) -> bool:
        if not self.results:
            return False

        return all(
            result.passed
            for result in self.results
        )

    @property
    def evaluator_count(
        self,
    ) -> int:
        return len(
            self.results,
        )

    @property
    def failed_evaluator_names(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            result.evaluator_name
            for result in self.results
            if not result.passed
        )

    def get_result(
        self,
        evaluator_name: str,
    ) -> AnswerEvaluationResult | None:
        normalized_name = (
            evaluator_name.strip()
        )

        if not normalized_name:
            raise ValueError(
                "Evaluator name cannot be empty"
            )

        for result in self.results:
            if (
                result.evaluator_name
                == normalized_name
            ):
                return result

        return None

    def to_dict(
        self,
    ) -> dict:
        return {
            "overall_score": (
                self.overall_score
            ),
            "passed": self.passed,
            "evaluator_count": (
                self.evaluator_count
            ),
            "failed_evaluator_names": list(
                self.failed_evaluator_names
            ),
            "results": [
                {
                    "evaluator_name": (
                        result.evaluator_name
                    ),
                    "score": result.score,
                    "passed": result.passed,
                    "explanation": (
                        result.explanation
                    ),
                }
                for result in self.results
            ],
        }