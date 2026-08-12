from src.domains.skills.data.skill_ontology import SKILL_ONTOLOGY
from src.domains.skills.services.skill_normalizer import SkillNormalizer


class SkillOntologyService:
    def __init__(
        self,
    ):
        self.normalizer = SkillNormalizer()

    def expand_skills(
        self,
        skills: list[str],
    ) -> set[str]:
        expanded: set[str] = set()

        for skill in skills:
            normalized_skill = self.normalizer.normalize(skill)

            expanded.add(normalized_skill)

            related_skills = SKILL_ONTOLOGY.get(
                normalized_skill,
                [],
            )

            for related_skill in related_skills:
                expanded.add(
                    self.normalizer.normalize(related_skill)
                )

        return expanded