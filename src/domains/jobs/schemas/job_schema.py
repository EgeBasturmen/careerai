from datetime import datetime

from pydantic import BaseModel


class JobCreateRequest(BaseModel):
    title: str
    company_name: str
    description: str
    location: str | None = None
    remote_type: str | None = None
    seniority: str | None = None
    external_id: str | None = None
    required_skills: list[str] | None = None
    source: str | None = "manual"
    source_url: str | None = None


class JobResponse(BaseModel):
    id: int
    title: str
    company_name: str
    location: str | None
    remote_type: str | None
    seniority: str | None
    description: str
    required_skills: list[str] | None
    source: str | None   
    source_url: str | None
    created_at: datetime
    external_id: str | None
    normalized_title: str | None
    normalized_company_name: str | None
    normalized_location: str | None
    fingerprint: str | None
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class JobSummary(BaseModel):
    job_id: int
    title: str
    company_name: str
    seniority: str | None
    required_skills: list[str]

