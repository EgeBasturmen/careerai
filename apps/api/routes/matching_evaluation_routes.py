from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from src.core.database.session import get_db
from src.core.security.dependencies import (
    get_current_user,
)
from src.domains.matching.repositories.matching_evaluation_run_repository import (
    MatchingEvaluationRunRepository,
)
from src.domains.matching.schemas.matching_evaluation_schema import (
    MatchingEvaluationComparisonResponse,
    MatchingEvaluationRunResponse,
)
from src.domains.matching.services.matching_evaluation_comparison_service import (
    MatchingEvaluationComparisonService,
)
from src.domains.users.models.user import User

from src.domains.matching.services.matching_evaluation_service import (
    MatchingEvaluationService,
)

router = APIRouter(
    prefix="/matching-evaluations",
    tags=["Matching Evaluations"],
)


@router.get(
    "/runs",
    response_model=list[
        MatchingEvaluationRunResponse
    ],
)
def list_matching_evaluation_runs(
    algorithm_version: str | None = None,
    dataset_version: str | None = None,
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
    repository = (
        MatchingEvaluationRunRepository(
            db,
        )
    )

    runs = repository.list_runs(
        algorithm_version=algorithm_version,
        dataset_version=dataset_version,
        limit=limit,
        offset=offset,
    )

    return [
        MatchingEvaluationRunResponse
        .model_validate(run)
        for run in runs
    ]


@router.get(
    "/compare",
    response_model=(
        MatchingEvaluationComparisonResponse
    ),
)
def compare_matching_evaluation_runs(
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
        MatchingEvaluationComparisonService(
            db,
        )
    )

    return service.compare(
        baseline_run_id=baseline_run_id,
        candidate_run_id=candidate_run_id,
    )


@router.post(
    "/run",
    response_model=MatchingEvaluationRunResponse,
)
def run_matching_evaluation(
    dataset_path: str,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
):
    service = MatchingEvaluationService(db)

    run = service.run(
        dataset_path=dataset_path,
    )

    return MatchingEvaluationRunResponse.model_validate(
        run
    )