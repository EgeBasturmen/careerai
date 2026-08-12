from src.domains.jobs.services.job_skill_extractor import (
    JobSkillExtractor,
)


class JobParser:
    def __init__(
        self,
    ):
        self.skill_extractor = JobSkillExtractor()

    def parse(
        self,
        description: str,
    ) -> dict:
        return {
            "required_skills": self.skill_extractor.extract(
                description,
            ),
            "seniority": self._extract_seniority(
                description,
            ),
            "remote_type": self._extract_remote_type(
                description,
            ),
        }

    def _extract_seniority(
        self,
        description: str,
    ) -> str | None:
        lower_description = description.lower()

        if "intern" in lower_description or "stajyer" in lower_description:
            return "intern"

        if "junior" in lower_description:
            return "junior"

        if "mid" in lower_description or "middle" in lower_description:
            return "mid"

        if "senior" in lower_description:
            return "senior"

        return None

    def _extract_remote_type(
        self,
        description: str,
    ) -> str | None:
        lower_description = description.lower()

        if "remote" in lower_description or "uzaktan" in lower_description:
            return "remote"

        if "hybrid" in lower_description or "hibrit" in lower_description:
            return "hybrid"

        if "onsite" in lower_description or "office" in lower_description or "ofis" in lower_description:
            return "onsite"

        return None