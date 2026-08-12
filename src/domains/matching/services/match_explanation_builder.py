class MatchExplanationBuilder:
    def build(
        self,
        final_score: float,
        skill_score: float,
        semantic_score: float,
        matched_skills: list[str],
        missing_skills: list[str],
    ) -> str:
        if final_score >= 80:
            level = "Strong match"
        elif final_score >= 60:
            level = "Good match"
        elif final_score >= 40:
            level = "Partial match"
        else:
            level = "Weak match"

        semantic_message = (
            "The candidate profile is semantically "
            "close to the job description."
            if semantic_score >= 70
            else
            "The semantic similarity with the job "
            "description is limited."
        )

        skill_message = (
            f"Skill compatibility is "
            f"{round(skill_score, 2)}%."
        )

        return (
            f"{level}. "
            f"{skill_message} "
            f"{semantic_message} "
            f"Matched skills: "
            f"{', '.join(matched_skills) or 'None'}. "
            f"Missing skills: "
            f"{', '.join(missing_skills) or 'None'}."
        )