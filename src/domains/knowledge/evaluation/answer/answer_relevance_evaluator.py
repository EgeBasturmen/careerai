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
from src.infrastructure.llm.base import (
    LLMClient,
)

from src.domains.knowledge.evaluation.answer.base_llm_answer_evaluator import (
    BaseLLMAnswerEvaluator,
)

class AnswerRelevanceEvaluator(
    BaseLLMAnswerEvaluator,
):
    PROMPT_NAME = (
        "knowledge-answer-relevance-evaluation"
    )

    PROMPT_VERSION = "v1"

    def __init__(
        self,
        llm_client: LLMClient,
        pass_threshold: float = 0.8,
    ) -> None:
        if not 0.0 <= pass_threshold <= 1.0:
            raise ValueError(
                "Pass threshold must be between 0.0 and 1.0"
            )

        self.llm_client = llm_client
        self.pass_threshold = pass_threshold

    @property
    def evaluator_name(
        self,
    ) -> str:
        return "answer_relevance"

    def evaluate(
        self,
        *,
        evaluation_context: AnswerEvaluationContext,
    ) -> AnswerEvaluationResult:
        self._validate_input(
            evaluation_context,
        )

        prompt = self._build_prompt(
            question=evaluation_context.question,
            answer=evaluation_context.answer,
        )

        raw_response = (
            self.llm_client.generate(
                prompt=prompt,
                prompt_name=self.PROMPT_NAME,
                prompt_version=self.PROMPT_VERSION,
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
            evaluator_name=self.evaluator_name,
            score=score,
            passed=(
                score >= self.pass_threshold
            ),
            explanation=explanation,
        )

    def _validate_input(
        self,
        evaluation_context: AnswerEvaluationContext,
    ) -> None:
        if not evaluation_context.question.strip():
            raise ValueError(
                "Question cannot be empty"
            )

        if not evaluation_context.answer.strip():
            raise ValueError(
                "Answer cannot be empty"
            )

    def _build_prompt(
        self,
        *,
        question: str,
        answer: str,
    ) -> str:
        return f"""
You are evaluating answer relevance.

Determine whether the answer directly addresses
the user's question.

Evaluation rules:
1. Evaluate only answer relevance.
2. Ignore factual correctness.
3. Ignore retrieved context.
4. Ignore citations.
5. Ignore whether claims are supported.
6. Do not penalize the answer for being concise.
7. Penalize irrelevant, incomplete, or evasive answers.
8. Return only valid JSON.
9. Do not include markdown or code fences.

Required JSON format:
{{
  "score": 0.0,
  "explanation": "Brief explanation"
}}

The score must be between 0.0 and 1.0:

- 1.0: The answer directly and completely
  answers the question.
- 0.7: The answer addresses the question
  but is partially incomplete.
- 0.3: The answer is only slightly related.
- 0.0: The answer does not address the question.

Question:
{question}

Answer:
{answer}
""".strip()

