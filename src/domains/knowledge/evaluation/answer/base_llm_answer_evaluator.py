import json
from abc import abstractmethod
from typing import Any

from src.domains.knowledge.evaluation.answer.base_answer_evaluator import (
    BaseAnswerEvaluator,
)


class BaseLLMAnswerEvaluator(
    BaseAnswerEvaluator,
):
    @abstractmethod
    def _build_prompt(
        self,
        **kwargs,
    ) -> str:
        raise NotImplementedError

    def _parse_response(
        self,
        raw_response: str,
    ) -> dict[str, Any]:
        normalized_response = raw_response.strip()

        if normalized_response.startswith(
            "```"
        ):
            normalized_response = (
                self._remove_code_fence(
                    normalized_response,
                )
            )

        try:
            payload = json.loads(
                normalized_response,
            )

        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM evaluator returned invalid JSON"
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):
            raise ValueError(
                "LLM evaluator response must be a JSON object"
            )

        return payload

    def _extract_score(
        self,
        payload: dict[str, Any],
    ) -> float:
        score = payload.get("score")

        if (
            isinstance(score, bool)
            or not isinstance(
                score,
                (int, float),
            )
        ):
            raise ValueError(
                "Score must be numeric"
            )

        normalized_score = float(score)

        if not (
            0.0
            <= normalized_score
            <= 1.0
        ):
            raise ValueError(
                "Score must be between 0.0 and 1.0"
            )

        return normalized_score

    def _extract_explanation(
        self,
        payload: dict[str, Any],
    ) -> str:
        explanation = payload.get(
            "explanation",
        )

        if (
            not isinstance(
                explanation,
                str,
            )
            or not explanation.strip()
        ):
            raise ValueError(
                "Explanation cannot be empty"
            )

        return explanation.strip()

    def _remove_code_fence(
        self,
        response: str,
    ) -> str:
        lines = response.splitlines()

        if (
            lines
            and lines[0].startswith("```")
        ):
            lines = lines[1:]

        if (
            lines
            and lines[-1].strip() == "```"
        ):
            lines = lines[:-1]

        return "\n".join(lines).strip()