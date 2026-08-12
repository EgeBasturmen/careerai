from src.domains.cv_improvement.schemas.cv_improvement_schema import (
    ImprovementSuggestion,
)


class ImprovementAgent:
    def generate(
        self,
        missing_skills: list[str],
        matched_skills: list[str],
        language:str="en",
    ) -> list[ImprovementSuggestion]:
        suggestions: list[ImprovementSuggestion] = []

        if language == "tr":
            return self._generate_tr(
                missing_skills=missing_skills,
                matched_skills=matched_skills,
            )

        for skill in missing_skills:
            suggestions.append(
                ImprovementSuggestion(
                    title=f"Build evidence for {skill}",
                    description=(
                        f"The selected job requires {skill}, but it is not visible "
                        f"in your CV. Do not add it as experience unless you actually "
                        f"know it. If you want to become a stronger candidate, learn "
                        f"the basics of {skill} and build a small project that proves it."
                    ),
                    priority="HIGH",
                )
            )

        for skill in matched_skills:
            suggestions.append(
                ImprovementSuggestion(
                    title=f"Make {skill} more visible",
                    description=(
                        f"Your CV already shows evidence of {skill}. Make it more "
                        f"visible by mentioning it in your summary, skills section, "
                        f"and related experience or project descriptions."
                    ),
                    priority="MEDIUM",
                )
            )

        if not missing_skills and matched_skills:
            suggestions.append(
                ImprovementSuggestion(
                    title="Tailor your CV wording to this job",
                    description=(
                        "You already match the core requirements. Improve your CV by "
                        "using language closer to the job description and highlighting "
                        "measurable outcomes."
                    ),
                    priority="LOW",
                )
            )

        return suggestions
    def _generate_tr(
        self,
        missing_skills: list[str],
        matched_skills: list[str],
    ) -> list[ImprovementSuggestion]:
        suggestions: list[ImprovementSuggestion] = []

        for skill in missing_skills:
            suggestions.append(
                ImprovementSuggestion(
                    title=f"{skill} için kanıt oluştur",
                    description=(
                        f"Seçilen iş ilanı {skill} becerisini istiyor ancak bu beceri "
                        f"CV'de net görünmüyor. Gerçek deneyimin yoksa bunu CV'ye "
                        f"deneyim gibi ekleme. Önce {skill} temelini öğrenip küçük "
                        f"bir proje veya somut çalışma ile kanıt oluştur."
                    ),
                    priority="HIGH",
                )
            )

        for skill in matched_skills:
            suggestions.append(
                ImprovementSuggestion(
                    title=f"{skill} becerisini daha görünür yap",
                    description=(
                        f"CV'de {skill} için bazı kanıtlar var. Bu beceriyi özet, "
                        f"yetenekler ve ilgili deneyim/proje açıklamalarında daha "
                        f"net görünür hale getir."
                    ),
                    priority="MEDIUM",
                )
            )

        if not missing_skills and matched_skills:
            suggestions.append(
                ImprovementSuggestion(
                    title="CV dilini bu ilana göre uyarlayın",
                    description=(
                        "Ana gereksinimlerle güçlü bir eşleşme var. CV'deki ifadeleri "
                        "ilan diline yaklaştırarak ve ölçülebilir çıktılar ekleyerek "
                        "daha güçlü hale getirebilirsin."
                    ),
                    priority="LOW",
                )
            )

        return suggestions