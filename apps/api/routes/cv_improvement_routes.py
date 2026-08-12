from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database.session import get_db
from src.core.security.dependencies import get_current_user
from src.domains.cv_improvement.schemas.cv_improvement_schema import (
    CVImprovementResponse,
    SavedCVImprovementResponse,
)
from src.domains.cv_improvement.services.cv_improvement_service import (
    CVImprovementService,
)
from src.domains.users.models.user import User
from fastapi import APIRouter, Depends, Query

router = APIRouter(
    prefix="/cv-improvements",
    tags=["CV Improvements"],
)


@router.get(
    "/resumes/{resume_id}/jobs/{job_id}",
    response_model=CVImprovementResponse,
)
def improve_cv_for_job(
    resume_id: int,
    job_id: int,
    current_user: User = Depends(get_current_user),
    language: str = Query(default="en", pattern="^(en|tr)$"),
    db: Session = Depends(get_db),
):
    service = CVImprovementService(db)

    return service.improve_for_job(
        current_user=current_user,
        resume_id=resume_id,
        job_id=job_id,
        language=language
    )

@router.get(
    "/resumes/{resume_id}/saved",
    response_model=list[SavedCVImprovementResponse],
)
def get_saved_cv_improvements(
    resume_id: int,
    language: str | None = Query(
        default=None,
        pattern="^(en|tr)$",
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CVImprovementService(db)

    return service.get_saved_improvements(
        current_user=current_user,
        resume_id=resume_id,
        language=language,
    )