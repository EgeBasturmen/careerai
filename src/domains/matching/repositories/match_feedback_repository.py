from sqlalchemy.orm import Session

from src.domains.matching.models.match_feedback import (
    MatchFeedback,
)


class MatchFeedbackRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def get_by_user_resume_job(
        self,
        user_id: int,
        resume_id: int,
        job_id: int,
    ) -> MatchFeedback | None:
        return (
            self.db.query(MatchFeedback)
            .filter(
                MatchFeedback.user_id == user_id,
                MatchFeedback.resume_id == resume_id,
                MatchFeedback.job_id == job_id,
            )
            .first()
        )

    def upsert(
        self,
        user_id: int,
        resume_id: int,
        job_id: int,
        relevance_grade: int,
        notes: str | None,
    ) -> MatchFeedback:
        existing = self.get_by_user_resume_job(
            user_id=user_id,
            resume_id=resume_id,
            job_id=job_id,
        )

        if existing is not None:
            existing.relevance_grade = relevance_grade
            existing.notes = notes

            self.db.commit()
            self.db.refresh(existing)

            return existing

        feedback = MatchFeedback(
            user_id=user_id,
            resume_id=resume_id,
            job_id=job_id,
            relevance_grade=relevance_grade,
            notes=notes,
        )

        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)

        return feedback

    def list_by_resume(
        self,
        user_id: int,
        resume_id: int,
    ) -> list[MatchFeedback]:
        return (
            self.db.query(MatchFeedback)
            .filter(
                MatchFeedback.user_id == user_id,
                MatchFeedback.resume_id == resume_id,
            )
            .order_by(
                MatchFeedback.updated_at.desc()
            )
            .all()
        )
    def list_all(
        self,
        minimum_feedback_per_resume: int = 1,
    ) -> list[MatchFeedback]:
        feedback_records = (
            self.db.query(MatchFeedback)
            .order_by(
                MatchFeedback.user_id.asc(),
                MatchFeedback.resume_id.asc(),
                MatchFeedback.job_id.asc(),
            )
            .all()
        )

        if minimum_feedback_per_resume <= 1:
            return feedback_records

        counts: dict[
            tuple[int, int],
            int,
        ] = {}

        for feedback in feedback_records:
            key = (
                feedback.user_id,
                feedback.resume_id,
            )

            counts[key] = counts.get(
                key,
                0,
            ) + 1

        return [
            feedback
            for feedback in feedback_records
            if counts[
                (
                    feedback.user_id,
                    feedback.resume_id,
                )
            ] >= minimum_feedback_per_resume
        ]
    
