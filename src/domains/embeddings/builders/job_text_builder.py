from src.domains.jobs.models.job import Job


class JobTextBuilder:
    def build(
        self,
        job: Job,
    ) -> str:
        sections: list[str] = []

        if job.title:
            sections.append(
                f"Job Title: {job.title}"
            )

        if job.company_name:
            sections.append(
                f"Company: {job.company_name}"
            )

        if job.seniority:
            sections.append(
                f"Seniority: {job.seniority}"
            )

        if job.remote_type:
            sections.append(
                f"Work Type: {job.remote_type}"
            )

        if job.location:
            sections.append(
                f"Location: {job.location}"
            )

        if job.required_skills:
            skill_lines = "\n".join(
                f"- {skill}"
                for skill in job.required_skills
            )

            sections.append(
                f"Required Skills:\n{skill_lines}"
            )

        if job.description:
            sections.append(
                f"Description:\n{job.description}"
            )

        return "\n\n".join(
            sections
        ).strip()