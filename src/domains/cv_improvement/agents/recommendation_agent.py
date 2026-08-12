from src.domains.cv_improvement.schemas.cv_improvement_schema import (
    ImprovementSuggestion,
)


class RecommendationAgent:
    def refine(
        self,
        suggestions: list[ImprovementSuggestion],
    ) -> list[ImprovementSuggestion]:
        priority_order = {
            "HIGH": 0,
            "MEDIUM": 1,
            "LOW": 2,
        }

        return sorted(
            suggestions,
            key=lambda item: priority_order.get(
                item.priority,
                99,
            ),
        )

    def build_summary(
        self,
        matched_skills: list[str],
        missing_skills: list[str],
    ) -> str:
        matched_count = len(matched_skills)
        missing_count = len(missing_skills)

        if matched_count == 0:
            return (
                "This job is currently a weak match. "
                "Your CV does not show the core skills required for this role yet."
            )

        if missing_count == 0:
            return (
                "This job is a strong match. "
                "Your CV already covers the main required skills, but the wording can still be tailored."
            )

        if matched_count >= missing_count:
            return (
                "This job is a partial-to-strong match. "
                "Your CV already shows several relevant strengths, but a few missing skills should be improved."
            )

        return (
            "This job is a partial match. "
            "Your CV has some relevant skills, but the missing requirements should be prioritized."
        )