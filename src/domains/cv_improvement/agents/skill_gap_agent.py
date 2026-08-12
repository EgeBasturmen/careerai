from src.domains.cv_improvement.schemas.cv_improvement_schema import (
    SkillGapResult,
)
from src.domains.skills.services.skill_normalizer import SkillNormalizer
from src.domains.skills.services.skill_ontology_service import (
    SkillOntologyService,
)


class SkillGapAgent:
    def __init__(
        self,
    ):
        self.normalizer = SkillNormalizer()
        self.ontology = SkillOntologyService()

    def analyze(
        self,
        resume_skills: list[str],
        job_required_skills: list[str],
    ) -> SkillGapResult:
        expanded_resume_skills = self.ontology.expand_skills(
            resume_skills,
        )

        matched_skills: list[str] = []
        missing_skills: list[str] = []

        for skill in job_required_skills:
            normalized_skill = self.normalizer.normalize(
                skill,
            )

            if normalized_skill in expanded_resume_skills:
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)

        return SkillGapResult(
            missing_skills=missing_skills,
            matched_skills=matched_skills,
        )