from src.domains.matching.ml.match_training_example import (
    MatchTrainingExample,
)
from src.domains.matching.models.match import Match
from src.domains.matching.models.match_feedback import (
    MatchFeedback,
)


class MatchFeatureExtractor:
    def extract(
        self,
        match: Match,
        feedback: MatchFeedback,
    ) -> MatchTrainingExample:
        score_breakdown = (
            match.score_breakdown
            or {}
        )

        matched_skills = (
            match.matched_skills
            or []
        )

        missing_skills = (
            match.missing_skills
            or []
        )

        matched_skill_count = self._get_int(
            score_breakdown,
            "matched_skill_count",
            fallback=len(
                matched_skills
            ),
        )

        missing_skill_count = self._get_int(
            score_breakdown,
            "missing_skill_count",
            fallback=len(
                missing_skills
            ),
        )

        required_skill_count = self._get_int(
            score_breakdown,
            "required_skill_count",
            fallback=(
                matched_skill_count
                + missing_skill_count
            ),
        )

        skill_match_ratio = self._safe_ratio(
            numerator=matched_skill_count,
            denominator=required_skill_count,
        )

        missing_skill_ratio = self._safe_ratio(
            numerator=missing_skill_count,
            denominator=required_skill_count,
        )

        skill_coverage_gap = max(
            0.0,
            min(
                1.0,
                1.0 - skill_match_ratio,
            ),
        )

        return MatchTrainingExample(
            user_id=feedback.user_id,
            resume_id=match.resume_id,
            job_id=match.job_id,
            algorithm_version=(
                match.algorithm_version
            ),
            skill_score=self._get_float(
                score_breakdown,
                "skill_score",
            ),
            semantic_score=self._get_float(
                score_breakdown,
                "semantic_score",
            ),
            reranker_score=self._get_float(
                score_breakdown,
                "reranker_score",
            ),
            seniority_score=self._get_float(
                score_breakdown,
                "seniority_score",
            ),
            location_score=self._get_float(
                score_breakdown,
                "location_score",
            ),
            matched_skill_count=matched_skill_count,
            missing_skill_count=missing_skill_count,
            required_skill_count=required_skill_count,

            skill_match_ratio=skill_match_ratio,
            missing_skill_ratio=missing_skill_ratio,
            skill_coverage_gap=skill_coverage_gap,
            match_score=float(
                match.match_score
            ),
            relevance_grade=int(
                feedback.relevance_grade
            ),
        )

    def _get_float(
        self,
        values: dict,
        key: str,
        fallback: float = 0.0,
    ) -> float:
        value = values.get(
            key,
            fallback,
        )

        try:
            return float(value)
        except (
            TypeError,
            ValueError,
        ):
            return fallback

    def _get_int(
        self,
        values: dict,
        key: str,
        fallback: int = 0,
    ) -> int:
        value = values.get(
            key,
            fallback,
        )

        try:
            return int(value)
        except (
            TypeError,
            ValueError,
        ):
            return fallback

    def _safe_ratio(
        self,
        *,
        numerator: int,
        denominator: int,
    ) -> float:
        if denominator <= 0:
            return 0.0

        ratio = numerator / denominator

        return max(
            0.0,
            min(
                float(ratio),
                1.0,
            ),
        )