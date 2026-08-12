from src.infrastructure.job_sources.base import (
    ExternalJob,
    JobSourceClient,
)


class FakeJobSource(JobSourceClient):
    @property
    def source_name(
        self,
    ) -> str:
        return "fake"

    def fetch_jobs(
        self,
    ) -> list[ExternalJob]:
        return [
            ExternalJob(
                external_id="fake-001",
                title="Junior Python Backend Developer",
                company_name="TechNova Ltd.",
                description=(
                    "We are looking for a junior Python backend developer. "
                    "Candidates should have experience with Python, FastAPI, "
                    "PostgreSQL, Redis and Docker. The role is hybrid."
                ),
                location="Istanbul",
                remote_type="hybrid",
                seniority="junior",
                source_url="https://example.com/jobs/fake-001",
            ),
            ExternalJob(
                external_id="fake-002",
                title="Human Resources Intern",
                company_name="PeoplePlus A.Ş.",
                description=(
                    "We are looking for a Human Resources intern. "
                    "The candidate should have knowledge of recruitment, "
                    "performance management and corporate communication."
                ),
                location="Istanbul",
                remote_type="onsite",
                seniority="intern",
                source_url="https://example.com/jobs/fake-002",
            ),
        ]