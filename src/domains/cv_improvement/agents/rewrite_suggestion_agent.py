from src.domains.cv_improvement.schemas.cv_improvement_schema import (
    CVRewriteSuggestion,
)


class RewriteSuggestionAgent:
    def generate(
        self,
        matched_skills: list[str],
        missing_skills: list[str],
        target_role: str | None,
        language:str="en",
    ) -> list[CVRewriteSuggestion]:
        suggestions: list[CVRewriteSuggestion] = []

        if language == "tr":
            return self._generate_tr(
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                target_role=target_role,
            )

        if matched_skills:
            skills_text = ", ".join(
                matched_skills
            )

            role_text = (
                target_role
                or "the target role"
            )

            suggestions.append(
                CVRewriteSuggestion(
                    section="Summary",
                    suggested_text=(
                        f"Candidate with experience related to {role_text}, "
                        f"with visible strengths in {skills_text}. "
                        f"Focused on applying these skills to role-specific business needs."
                    ),
                    reason=(
                        "This rewrite highlights skills that are already visible "
                        "in the CV and aligns them with the selected job."
                    ),
                )
            )

            suggestions.append(
                CVRewriteSuggestion(
                    section="Skills",
                    suggested_text=(
                        "Relevant Skills: "
                        f"{skills_text}"
                    ),
                    reason=(
                        "Grouping matched skills under a visible skills section "
                        "helps recruiters quickly identify fit."
                    ),
                )
            )

        if missing_skills:
            missing_text = ", ".join(
                missing_skills
            )

            suggestions.append(
                CVRewriteSuggestion(
                    section="Development Plan",
                    suggested_text=(
                        f"To become a stronger candidate for this role, "
                        f"focus on improving: {missing_text}."
                    ),
                    reason=(
                        "Missing skills should not be added as experience. "
                        "They should be shown as a learning or development plan until real experience exists."
                    ),
                )
            )

        return suggestions
    
    def _generate_tr(
        self,
        matched_skills: list[str],
        missing_skills: list[str],
        target_role: str | None,
    ) -> list[CVRewriteSuggestion]:
        suggestions: list[CVRewriteSuggestion] = []

        if matched_skills:
            skills_text = ", ".join(matched_skills)
            role_text = target_role or "hedef rol"

            suggestions.append(
                CVRewriteSuggestion(
                    section="Özet",
                    suggested_text=(
                        f"{role_text} alanına yönelik deneyim ve becerilere sahip aday. "
                        f"CV'de öne çıkan güçlü beceriler: {skills_text}. "
                        f"Bu becerileri iş ihtiyaçlarına uygulamaya odaklanır."
                    ),
                    reason=(
                        "Bu öneri CV'de zaten görünen becerileri öne çıkarır ve "
                        "seçilen iş ilanıyla daha uyumlu hale getirir."
                    ),
                )
            )

            suggestions.append(
                CVRewriteSuggestion(
                    section="Yetenekler",
                    suggested_text=f"İlgili Yetenekler: {skills_text}",
                    reason=(
                        "Eşleşen becerileri ayrı ve görünür bir yetenekler alanında "
                        "toplamak işe alım yapan kişinin uygunluğu hızlı görmesini sağlar."
                    ),
                )
            )

        if missing_skills:
            missing_text = ", ".join(missing_skills)

            suggestions.append(
                CVRewriteSuggestion(
                    section="Gelişim Planı",
                    suggested_text=(
                        f"Bu rol için daha güçlü bir aday olmak adına şu alanları "
                        f"geliştirmeye odaklan: {missing_text}."
                    ),
                    reason=(
                        "Eksik beceriler deneyim gibi CV'ye eklenmemeli. Gerçek deneyim "
                        "oluşana kadar öğrenme ve gelişim planı olarak gösterilmelidir."
                    ),
                )
            )

        return suggestions