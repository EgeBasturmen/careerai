from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database.session import get_db
from src.core.security.dependencies import (
    get_current_user,
)
from src.domains.matching.schemas.match_feedback_schema import (
    MatchFeedbackRequest,
    MatchFeedbackResponse,
    MatchFeedbackSummaryResponse,
)
from src.domains.matching.services.match_feedback_service import (
    MatchFeedbackService,
)
from src.domains.users.models.user import User


router = APIRouter(
    prefix="/match-feedback",
    tags=["Match Feedback"],
)


@router.put(
    "/resumes/{resume_id}/jobs/{job_id}",
    response_model=MatchFeedbackResponse,
)
def save_match_feedback(
    resume_id: int,
    job_id: int,
    request: MatchFeedbackRequest,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
):
    service = MatchFeedbackService(
        db,
    )

    return service.save_feedback(
        current_user=current_user,
        resume_id=resume_id,
        job_id=job_id,
        request=request,
    )


@router.get(
    "/resumes/{resume_id}",
    response_model=MatchFeedbackSummaryResponse,
)
def get_resume_match_feedback(
    resume_id: int,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
):
    service = MatchFeedbackService(
        db,
    )

    return service.get_resume_feedback(
        current_user=current_user,
        resume_id=resume_id,
    )