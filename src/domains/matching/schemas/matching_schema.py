from datetime import datetime

from pydantic import BaseModel


class MatchScoreBreakdown(BaseModel):
    skill_score: float
    semantic_score: float
    seniority_score: float
    location_score: float

    reranker_score: float 
    reranker_raw_score: float | None = None


    matched_skill_count: int
    missing_skill_count: int
    required_skill_count: int

class MatchingConfigurationResponse(BaseModel):
    skill_weight: float
    semantic_weight: float
    seniority_weight: float
    location_weight: float
    reranker_weight: float

    minimum_similarity: float
    candidate_limit: int
    algorithm_version: str


class JobMatchResponse(BaseModel):
    job_id: int
    title: str
    company_name: str
    match_score: float
    score_breakdown: MatchScoreBreakdown
    matched_skills: list[str]
    missing_skills: list[str]
    explanation: str


class ResumeMatchesResponse(BaseModel):
    resume_id: int

    total_candidates: int
    returned_count: int

    limit: int
    offset: int

    configuration: MatchingConfigurationResponse

    matches: list[JobMatchResponse]


class SavedMatchResponse(BaseModel):
    id: int
    resume_id: int
    job_id: int
    match_score: float
    score_breakdown: dict
    matched_skills: list[str]
    missing_skills: list[str]
    created_at: datetime
    algorithm_version: str

    model_config = {
        "from_attributes": True,
    }