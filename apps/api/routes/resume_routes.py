from fastapi import APIRouter
from fastapi import Depends
from fastapi import UploadFile

from sqlalchemy.orm import Session

from src.core.database.session import get_db

from src.core.security.dependencies import (
    get_current_user,
)

from src.domains.resumes.services.resume_service import (
    ResumeService,
)

from src.domains.users.models.user import User
from src.domains.resumes.schemas.resume_schema import ResumeResponse
from fastapi import Query


router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"],
)


@router.post("/upload")
def upload_resume(
    file: UploadFile,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
):

    service = ResumeService(db)

    return service.upload_resume(
        current_user=current_user,
        file=file,
    )


@router.get(
    "/{resume_id}",
    response_model=ResumeResponse,
)
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ResumeService(db)

    return service.get_resume(
        current_user=current_user,
        resume_id=resume_id,
    )

