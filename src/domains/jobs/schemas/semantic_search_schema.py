from pydantic import BaseModel, Field


class SemanticJobMatchResponse(BaseModel):
    job_id: int
    title: str
    company_name: str

    location: str | None
    remote_type: str | None
    seniority: str | None

    required_skills: list[str]

    similarity_score: float = Field(
        ge=-1.0,
        le=1.0,
    )