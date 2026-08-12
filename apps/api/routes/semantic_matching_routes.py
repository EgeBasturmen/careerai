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
from src.domains.embeddings.schemas.semantic_search_schema import (
    SemanticJobMatchResponse,
)
from src.domains.embeddings.services.semantic_matching_service import (
    SemanticMatchingService,
)
from src.domains.users.models.user import User


router = APIRouter(
    prefix="/semantic-matches",
    tags=["Semantic Matches"],
)


@router.get(
    "/resumes/{resume_id}/jobs",
    response_model=list[
        SemanticJobMatchResponse
    ],
)
def find_semantic_jobs_for_resume(
    resume_id: int,
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    minimum_similarity: float | None = Query(
        default=None,
        ge=-1.0,
        le=1.0,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
):
    service = SemanticMatchingService(
        db,
    )

    return service.find_jobs_for_resume(
        current_user=current_user,
        resume_id=resume_id,
        limit=limit,
        minimum_similarity=minimum_similarity,
    )