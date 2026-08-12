from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class AnswerEvaluationResult:
    evaluator_name: str
    score: float
    passed: bool
    explanation: str

    def __post_init__(
        self,
    ) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(
                "Evaluation score must be "
                "between 0.0 and 1.0"
            )

        if not self.evaluator_name.strip():
            raise ValueError(
                "Evaluator name cannot be empty"
            )

        if not self.explanation.strip():
            raise ValueError(
                "Evaluation explanation "
                "cannot be empty"
            )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "evaluator_name": self.evaluator_name,
            "score": self.score,
            "passed": self.passed,
            "explanation": self.explanation,
        }