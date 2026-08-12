from datetime import datetime

from pydantic import BaseModel, Field


class MatchFeedbackRequest(BaseModel):
    relevance_grade: int = Field(
        ge=0,
        le=3,
    )

    notes: str | None = Field(
        default=None,
        max_length=1000,
    )


class MatchFeedbackResponse(BaseModel):
    id: int

    user_id: int
    resume_id: int
    job_id: int

    relevance_grade: int
    notes: str | None

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class MatchFeedbackSummaryResponse(BaseModel):
    resume_id: int
    total_feedback_count: int

    irrelevant_count: int
    low_relevance_count: int
    relevant_count: int
    highly_relevant_count: int

    feedback: list[MatchFeedbackResponse]