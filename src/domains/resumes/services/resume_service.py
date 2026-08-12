import shutil
from pathlib import Path

from fastapi import UploadFile
import hashlib
from sqlalchemy.orm import Session
from uuid import uuid4
from src.domains.resumes.repositories.resume_repository import (
    ResumeRepository,
)
from src.infrastructure.queue.resume_tasks import (
    process_resume,
)
from src.domains.users.models.user import User

from fastapi import HTTPException, status
from src.domains.resumes.schemas.resume_schema import ResumeResponse

UPLOAD_DIR = Path(
    "uploads/resumes"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)
class ResumeService:
    def __init__(
        self,
        db: Session,
    ):
        self.repository = ResumeRepository(db)

    def upload_resume(
        self,
        current_user: User,
        file: UploadFile,
    ):
        safe_filename = Path(
            file.filename or "resume.pdf"
        ).name

        filename = (
            f"{current_user.id}_"
            f"{uuid4().hex}_"
            f"{safe_filename}"
        )

        file_path = (
            UPLOAD_DIR / filename
        )

        with open(
            file_path,
            "wb",
        ) as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
            )
        file_hash = self._calculate_file_hash(
            file_path,
        )
        resume = self.repository.create(
            user_id=current_user.id,
            original_filename=(
                file.filename or safe_filename
            ),
            storage_path=str(file_path),
            file_hash=file_hash,
            source="user_upload",
        )

        process_resume.delay(
            resume.id,
        )

        return resume
    
    def get_resume(
        self,
        current_user: User,
        resume_id: int,
    ) -> ResumeResponse:

        resume = self.repository.get_by_id_and_user(
            resume_id=resume_id,
            user_id=current_user.id,
        )

        if resume is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

        return ResumeResponse.model_validate(resume)

    @staticmethod
    def _calculate_file_hash(
        file_path: Path,
    ) -> str:
        hash_calculator = hashlib.sha256()

        with file_path.open("rb") as file:
            for chunk in iter(
                lambda: file.read(1024 * 1024),
                b"",
            ):
                hash_calculator.update(chunk)

        return hash_calculator.hexdigest()