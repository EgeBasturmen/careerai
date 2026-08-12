from typing import Any


class ResumeTextBuilder:
    def build(
        self,
        parsed_profile: dict[str, Any],
    ) -> str:
        sections: list[str] = []

        self._append_target_role(
            sections,
            parsed_profile,
        )

        self._append_seniority(
            sections,
            parsed_profile,
        )

        self._append_skills(
            sections,
            parsed_profile,
        )

        self._append_experience(
            sections,
            parsed_profile,
        )

        self._append_education(
            sections,
            parsed_profile,
        )

        return "\n\n".join(sections).strip()

    def _append_target_role(
        self,
        sections: list[str],
        profile: dict[str, Any],
    ) -> None:
        target_role = profile.get(
            "target_role",
        )

        if target_role:
            sections.append(
                f"Target Role: {target_role}"
            )

    def _append_seniority(
        self,
        sections: list[str],
        profile: dict[str, Any],
    ) -> None:
        seniority = profile.get(
            "seniority",
        )

        if seniority:
            sections.append(
                f"Seniority: {seniority}"
            )

    def _append_skills(
        self,
        sections: list[str],
        profile: dict[str, Any],
    ) -> None:
        skills = profile.get(
            "skills",
            [],
        )

        if not skills:
            return

        skill_lines = "\n".join(
            f"- {skill}"
            for skill in skills
        )

        sections.append(
            f"Skills:\n{skill_lines}"
        )

    def _append_experience(
        self,
        sections: list[str],
        profile: dict[str, Any],
    ) -> None:
        experience = profile.get(
            "experience",
        )

        if experience:
            sections.append(
                f"Experience:\n{experience}"
            )

    def _append_education(
        self,
        sections: list[str],
        profile: dict[str, Any],
    ) -> None:
        education = profile.get(
            "education",
        )

        if education:
            sections.append(
                f"Education:\n{education}"
            )