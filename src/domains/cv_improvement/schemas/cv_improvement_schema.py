from pydantic import BaseModel
from datetime import datetime
from src.domains.jobs.schemas.job_schema import JobSummary

class ResumeAnalysisResult(BaseModel):
    skills: list[str]
    target_role: str | None
    seniority: str | None


class SkillGapResult(BaseModel):
    missing_skills: list[str]
    matched_skills: list[str]


class StrengthResult(BaseModel):
    strengths: list[str]


class ImprovementSuggestion(BaseModel):
    title: str
    description: str
    priority: str

class CVRewriteSuggestion(BaseModel):
    section: str
    suggested_text: str
    reason: str
    
class LLMMetadata(BaseModel):
    provider:str
    prompt_name:str
    prompt_version:str


class CVImprovementResponse(BaseModel):
    resume_id: int
    job_id: int
    summary:str
    rewrite_suggestions: list[CVRewriteSuggestion]
    job_summary: JobSummary
    llm_metadata: LLMMetadata | None = None
    language:str
    

    resume_analysis: ResumeAnalysisResult
    skill_gap: SkillGapResult
    strengths: StrengthResult
    suggestions: list[ImprovementSuggestion]

class SavedCVImprovementResponse(BaseModel):
    id: int
    resume_id: int
    job_id: int
    result: dict
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }

