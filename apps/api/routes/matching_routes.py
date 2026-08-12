from fastapi import APIRouter
from fastapi import Depends
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.core.database.session import get_db
from src.core.security.dependencies import get_current_user
from src.domains.matching.schemas.matching_schema import (
    ResumeMatchesResponse,
    SavedMatchResponse,
)
from src.domains.matching.services.matching_service import (
    MatchingService,
)
from src.domains.users.models.user import User

from src.core.config.settings import settings

router = APIRouter(
    prefix="/matches",
    tags=["Matches"],
)

@router.get(
    "/resumes/{resume_id}",
    response_model=ResumeMatchesResponse,
)
def match_resume_to_jobs(
    resume_id: int,
    seniority: str | None = None,
    remote_type: str | None = None,
    location: str | None = None,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    candidate_limit: int = Query(
        default=(
            settings.matching_default_candidate_limit
        ),
        ge=10,
        le=500,
    ),
    minimum_similarity: float | None = Query(
        default=(
            settings.matching_default_minimum_similarity
        ),
        ge=-1.0,
        le=1.0,
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MatchingService(db)

    return service.match_resume_to_jobs(
        current_user=current_user,
        resume_id=resume_id,
        seniority=seniority,
        remote_type=remote_type,
        location=location,
        limit=limit,
        offset=offset,
        candidate_limit=candidate_limit,
        minimum_similarity=minimum_similarity
    )

@router.get(
    "/resumes/{resume_id}/saved",
    response_model=list[SavedMatchResponse],
)
def get_saved_matches(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MatchingService(db)

    return service.get_saved_matches(
        current_user=current_user,
        resume_id=resume_id,
    )