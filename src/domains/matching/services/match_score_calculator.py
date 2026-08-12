from src.core.config.settings import settings


class MatchScoreCalculator:
    def __init__(
        self,
    ):
        self.skill_weight = (
            settings.matching_skill_weight
        )

        self.semantic_weight = (
            settings.matching_semantic_weight
        )

        self.reranker_weight = (
            settings.matching_reranker_weight
        )

        self.seniority_weight = (
            settings.matching_seniority_weight
        )

        self.location_weight = (
            settings.matching_location_weight
        )

        self._validate_weights()

    def calculate_final_score(
        self,
        skill_score: float,
        semantic_score: float,
        seniority_score: float,
        location_score: float,
        reranker_score: float,
    ) -> float:
        final_score = (
            skill_score * self.skill_weight
            + semantic_score * self.semantic_weight
            + reranker_score * self.reranker_weight
            + seniority_score * self.seniority_weight
            + location_score * self.location_weight
        )

        return self._clamp_score(
            final_score,
        )

    def calculate_skill_score(
        self,
        matched_count: int,
        required_count: int,
    ) -> float:
        if required_count == 0:
            return 0.0

        score = (
            matched_count
            / required_count
        ) * 100

        return self._clamp_score(
            score,
        )

    def calculate_semantic_score(
        self,
        similarity: float | None,
    ) -> float:
        if similarity is None:
            return 0.0

        return self._clamp_score(
            similarity * 100,
        )

    def calculate_reranker_score(
        self,
        reranker_score: float | None,
    ) -> float:
        if reranker_score is None:
            return 0.0

        return self._clamp_score(
            reranker_score * 100,
        )

    def calculate_seniority_score(
        self,
        resume_profile: dict,
        job_seniority: str | None,
    ) -> float:
        if not job_seniority:
            return 60.0

        resume_seniority = (
            resume_profile.get("seniority")
            or ""
        ).strip().lower()

        normalized_job_seniority = (
            job_seniority
            .strip()
            .lower()
        )

        if not resume_seniority:
            return 50.0

        if (
            resume_seniority
            == normalized_job_seniority
        ):
            return 100.0

        seniority_levels = {
            "intern": 0,
            "junior": 1,
            "mid": 2,
            "middle": 2,
            "senior": 3,
            "lead": 4,
        }

        resume_level = seniority_levels.get(
            resume_seniority,
        )

        job_level = seniority_levels.get(
            normalized_job_seniority,
        )

        if (
            resume_level is None
            or job_level is None
        ):
            return 50.0

        difference = abs(
            resume_level - job_level
        )

        scores_by_difference = {
            0: 100.0,
            1: 70.0,
            2: 35.0,
        }

        return scores_by_difference.get(
            difference,
            10.0,
        )

    def calculate_location_score(
        self,
        resume_profile: dict,
        job_location: str | None,
        remote_type: str | None,
    ) -> float:
        normalized_remote_type = (
            remote_type
            or ""
        ).strip().lower()

        if normalized_remote_type == "remote":
            return 100.0

        resume_location = (
            resume_profile.get("location")
            or ""
        ).strip().lower()

        normalized_job_location = (
            job_location
            or ""
        ).strip().lower()

        if not normalized_job_location:
            return 60.0

        if not resume_location:
            if normalized_remote_type == "hybrid":
                return 70.0

            return 50.0

        if (
            resume_location
            in normalized_job_location
            or normalized_job_location
            in resume_location
        ):
            return 100.0

        if normalized_remote_type == "hybrid":
            return 50.0

        return 20.0

    def apply_relevance_gate(
        self,
        final_score: float,
        skill_score: float,
        semantic_score: float,
    ) -> float:
        if (
            skill_score
            < settings.matching_low_skill_threshold
            and semantic_score
            < settings.matching_low_semantic_threshold
        ):
            return min(
                final_score,
                settings.matching_low_relevance_cap,
            )

        if (
            skill_score == 0.0
            and semantic_score
            < settings.matching_zero_skill_semantic_threshold
        ):
            return min(
                final_score,
                settings.matching_zero_skill_cap,
            )

        return self._clamp_score(
            final_score,
        )

    def _validate_weights(
        self,
    ) -> None:
        total_weight = (
            self.skill_weight
            + self.semantic_weight
            + self.reranker_weight
            + self.seniority_weight
            + self.location_weight
        )

        if abs(total_weight - 1.0) > 0.0001:
            raise ValueError(
                "Matching weights must sum to 1.0. "
                f"Current total: {total_weight}"
            )

        weights = [
            self.skill_weight,
            self.semantic_weight,
            self.seniority_weight,
            self.location_weight,
        ]

        if any(
            weight < 0
            for weight in weights
        ):
            raise ValueError(
                "Matching weights cannot be negative"
            )

    def _clamp_score(
        self,
        score: float,
    ) -> float:
        return max(
            0.0,
            min(score, 100.0),
        )

    def calculate_remote_score(
        self,
        resume_profile: dict,
        job_remote_type: str | None,
    ) -> float:

        if not job_remote_type:
            return 50.0

        remote_type = (
            job_remote_type
            .strip()
            .lower()
        )

        preference = (
            resume_profile.get(
                "remote_preference"
            )
            or ""
        ).lower()


        if not preference:
            return 50.0


        if preference == remote_type:
            return 100.0


        if (
            preference == "hybrid"
            and remote_type == "remote"
        ):
            return 80.0


        return 30.0