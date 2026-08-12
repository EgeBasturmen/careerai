import json
from typing import Any

from src.domains.knowledge.evaluation.answer.answer_evaluation_context import (
    AnswerEvaluationContext,
)
from src.domains.knowledge.evaluation.answer.answer_evaluation_result import (
    AnswerEvaluationResult,
)
from src.domains.knowledge.evaluation.answer.base_answer_evaluator import (
    BaseAnswerEvaluator,
)
from src.domains.knowledge.evaluation.answer.base_llm_answer_evaluator import (
    BaseLLMAnswerEvaluator,
)
from src.infrastructure.llm.base import (
    LLMClient,
)


class FaithfulnessEvaluator(
    BaseLLMAnswerEvaluator,
):
    PROMPT_NAME = (
        "knowledge-answer-faithfulness-evaluation"
    )

    PROMPT_VERSION = "v1"

    def __init__(
        self,
        llm_client: LLMClient,
        pass_threshold: float = 0.8,
    ) -> None:
        if not 0.0 <= pass_threshold <= 1.0:
            raise ValueError(
                "Pass threshold must be "
                "between 0.0 and 1.0"
            )

        self.llm_client = llm_client
        self.pass_threshold = pass_threshold

    @property
    def evaluator_name(
        self,
    ) -> str:
        return "faithfulness"

    def evaluate(
        self,
        *,
        evaluation_context: (
            AnswerEvaluationContext
        ),
    ) -> AnswerEvaluationResult:
        self._validate_input(
            evaluation_context,
        )

        prompt = self._build_prompt(
            question=(
                evaluation_context.question
            ),
            answer=(
                evaluation_context.answer
            ),
            retrieved_context=(
                evaluation_context
                .retrieved_context
            ),
        )

        raw_response = (
            self.llm_client.generate(
                prompt=prompt,
                prompt_name=(
                    self.PROMPT_NAME
                ),
                prompt_version=(
                    self.PROMPT_VERSION
                ),
            )
        )

        payload = self._parse_response(
            raw_response,
        )

        score = self._extract_score(
            payload,
        )

        explanation = (
            self._extract_explanation(
                payload,
            )
        )

        return AnswerEvaluationResult(
            evaluator_name=(
                self.evaluator_name
            ),
            score=score,
            passed=(
                score
                >= self.pass_threshold
            ),
            explanation=explanation,
        )

    def _validate_input(
        self,
        evaluation_context: (
            AnswerEvaluationContext
        ),
    ) -> None:
        if not (
            evaluation_context
            .question
            .strip()
        ):
            raise ValueError(
                "Question cannot be empty"
            )

        if not (
            evaluation_context
            .answer
            .strip()
        ):
            raise ValueError(
                "Answer cannot be empty"
            )

        if not (
            evaluation_context
            .retrieved_context
            .strip()
        ):
            raise ValueError(
                "Retrieved context "
                "cannot be empty"
            )

    def _build_prompt(
        self,
        *,
        question: str,
        answer: str,
        retrieved_context: str,
    ) -> str:
        return f"""
You are evaluating the faithfulness of a RAG answer.

Determine whether every factual claim in the answer is supported by the
retrieved context.

Evaluation rules:
1. Use only the retrieved context.
2. Do not use outside knowledge.
3. A claim is faithful only if it is directly supported by the context.
4. Unsupported or contradictory claims must reduce the score.
5. Return only valid JSON.
6. Do not include markdown or code fences.

Required JSON format:
{{
  "score": 0.0,
  "explanation": "Brief explanation"
}}

The score must be between 0.0 and 1.0:
- 1.0: all factual claims are supported
- 0.5: some claims are supported
- 0.0: claims are unsupported or contradict the context

Question:
{question}

Retrieved context:
{retrieved_context}

Answer:
{answer}
""".strip()

