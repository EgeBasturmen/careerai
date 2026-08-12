from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.domains.jobs.repositories.job_repository import (
    JobRepository,
)
from src.domains.matching.repositories.match_feedback_repository import (
    MatchFeedbackRepository,
)
from src.domains.matching.schemas.match_feedback_schema import (
    MatchFeedbackRequest,
    MatchFeedbackResponse,
    MatchFeedbackSummaryResponse,
)
from src.domains.resumes.repositories.resume_repository import (
    ResumeRepository,
)
from src.domains.users.models.user import User


class MatchFeedbackService:
    def __init__(
        self,
        db: Session,
    ):
        self.resume_repository = ResumeRepository(db)
        self.job_repository = JobRepository(db)

        self.feedback_repository = (
            MatchFeedbackRepository(db)
        )

    def save_feedback(
        self,
        current_user: User,
        resume_id: int,
        job_id: int,
        request: MatchFeedbackRequest,
    ) -> MatchFeedbackResponse:
        resume = (
            self.resume_repository
            .get_by_id_and_user(
                resume_id=resume_id,
                user_id=current_user.id,
            )
        )

        if resume is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

        job = self.job_repository.get_by_id(
            job_id,
        )

        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

        feedback = self.feedback_repository.upsert(
            user_id=current_user.id,
            resume_id=resume.id,
            job_id=job.id,
            relevance_grade=request.relevance_grade,
            notes=request.notes,
        )

        return MatchFeedbackResponse.model_validate(
            feedback
        )

    def get_resume_feedback(
        self,
        current_user: User,
        resume_id: int,
    ) -> MatchFeedbackSummaryResponse:
        resume = (
            self.resume_repository
            .get_by_id_and_user(
                resume_id=resume_id,
                user_id=current_user.id,
            )
        )

        if resume is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

        feedback_records = (
            self.feedback_repository.list_by_resume(
                user_id=current_user.id,
                resume_id=resume.id,
            )
        )

        return MatchFeedbackSummaryResponse(
            resume_id=resume.id,
            total_feedback_count=len(
                feedback_records
            ),
            irrelevant_count=self._count_grade(
                feedback_records,
                grade=0,
            ),
            low_relevance_count=self._count_grade(
                feedback_records,
                grade=1,
            ),
            relevant_count=self._count_grade(
                feedback_records,
                grade=2,
            ),
            highly_relevant_count=self._count_grade(
                feedback_records,
                grade=3,
            ),
            feedback=[
                MatchFeedbackResponse.model_validate(
                    feedback
                )
                for feedback in feedback_records
            ],
        )

    def _count_grade(
        self,
        feedback_records: list,
        grade: int,
    ) -> int:
        return sum(
            1
            for feedback in feedback_records
            if feedback.relevance_grade == grade
        )