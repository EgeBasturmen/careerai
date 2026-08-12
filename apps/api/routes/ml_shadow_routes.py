from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database.session import get_db
from src.core.security.dependencies import (
    get_current_user,
)
from src.domains.matching.schemas.ml_shadow_comparison_schema import (
    MLShadowComparisonResponse,
)
from src.domains.matching.services.ml_shadow_comparison_service import (
    MLShadowComparisonService,
)
from src.domains.users.models.user import User

from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from src.domains.matching.repositories.ml_shadow_evaluation_run_repository import (
    MLShadowEvaluationRunRepository,
)
from src.domains.matching.schemas.ml_shadow_evaluation_schema import (
    MLShadowEvaluationRunResponse,
)
from fastapi import HTTPException

from src.domains.resumes.repositories.resume_repository import (
    ResumeRepository,
)
from src.domains.matching.schemas.ml_shadow_evaluation_comparison_schema import (
    MLShadowEvaluationRunComparisonResponse,
)
from src.domains.matching.services.ml_shadow_evaluation_comparison_service import (
    MLShadowEvaluationComparisonService,
)
router = APIRouter(
    prefix="/ml-shadow",
    tags=["ML Shadow"],
)


@router.get(
    "/resumes/{resume_id}/comparison",
    response_model=MLShadowComparisonResponse,
)
def compare_ml_shadow_for_resume(
    resume_id: int,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
):
    service = MLShadowComparisonService(
        db,
    )

    return service.compare_for_resume(
        current_user=current_user,
        resume_id=resume_id,
    )

@router.post(
    "/resumes/{resume_id}/evaluation-runs",
    response_model=MLShadowEvaluationRunResponse,
)
def create_ml_shadow_evaluation_run(
    resume_id: int,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
):
    service = MLShadowComparisonService(
        db,
    )

    return (
        service.compare_and_save_for_resume(
            current_user=current_user,
            resume_id=resume_id,
        )
    )
@router.get(
    "/resumes/{resume_id}/evaluation-runs",
    response_model=list[
        MLShadowEvaluationRunResponse
    ],
)
def list_ml_shadow_evaluation_runs(
    resume_id: int,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
):
    resume_repository = ResumeRepository(
        db,
    )

    resume = (
        resume_repository.get_by_id_and_user(
            resume_id=resume_id,
            user_id=current_user.id,
        )
    )

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found",
        )

    repository = (
        MLShadowEvaluationRunRepository(
            db,
        )
    )

    runs = repository.list_by_resume(
        user_id=current_user.id,
        resume_id=resume.id,
        limit=limit,
        offset=offset,
    )

    return [
        MLShadowEvaluationRunResponse
        .model_validate(run)
        for run in runs
    ]

@router.get(
    "/evaluation-runs/compare",
    response_model=(
        MLShadowEvaluationRunComparisonResponse
    ),
)
def compare_ml_shadow_evaluation_runs(
    baseline_run_id: int = Query(
        ge=1,
    ),
    candidate_run_id: int = Query(
        ge=1,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
):
    service = (
        MLShadowEvaluationComparisonService(
            db,
        )
    )

    return service.compare(
        current_user=current_user,
        baseline_run_id=baseline_run_id,
        candidate_run_id=candidate_run_id,
    )