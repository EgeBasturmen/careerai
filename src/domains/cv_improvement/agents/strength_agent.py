from src.domains.cv_improvement.schemas.cv_improvement_schema import (
    StrengthResult,
)


class StrengthAgent:
    def analyze(
        self,
        matched_skills: list[str],
    ) -> StrengthResult:
        strengths = [
            f"{skill} is aligned with the selected job."
            for skill in matched_skills
        ]

        return StrengthResult(
            strengths=strengths,
        )