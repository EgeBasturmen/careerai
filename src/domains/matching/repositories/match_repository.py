from sqlalchemy import func
from sqlalchemy.orm import Session

from src.domains.matching.models.match import (
    Match,
)


class MatchRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def get_by_resume_and_job(
        self,
        resume_id: int,
        job_id: int,
    ) -> Match | None:
        return (
            self.db.query(Match)
            .filter(
                Match.resume_id == resume_id,
                Match.job_id == job_id,
            )
            .first()
        )

    def get_by_id(
        self,
        match_id: int,
    ) -> Match | None:
        return (
            self.db.query(Match)
            .filter(
                Match.id == match_id,
            )
            .first()
        )

    def upsert(
        self,
        resume_id: int,
        job_id: int,
        match_score: float,
        score_breakdown: dict,
        matched_skills: list[str],
        missing_skills: list[str],
        algorithm_version: str,
        ml_predicted_relevance: float | None = None,
        ml_predicted_grade: int | None = None,
        ml_model_name: str | None = None,
        ml_model_version: str | None = None,
        ml_feature_set_identifier: str | None = None,
        ml_prediction_status: str | None = None,
        ml_prediction_error: str | None = None,
    ) -> Match:
        existing_match = (
            self.get_by_resume_and_job(
                resume_id=resume_id,
                job_id=job_id,
            )
        )

        if existing_match is not None:
            existing_match.match_score = (
                match_score
            )

            existing_match.score_breakdown = (
                score_breakdown
            )

            existing_match.matched_skills = (
                matched_skills
            )

            existing_match.missing_skills = (
                missing_skills
            )

            existing_match.algorithm_version = (
                algorithm_version
            )

            existing_match.ml_predicted_relevance = (
                ml_predicted_relevance
            )

            existing_match.ml_predicted_grade = (
                ml_predicted_grade
            )

            existing_match.ml_model_name = (
                ml_model_name
            )

            existing_match.ml_model_version = (
                ml_model_version
            )

            existing_match.ml_feature_set_identifier = (
                ml_feature_set_identifier
            )

            existing_match.ml_prediction_status = (
                ml_prediction_status
            )

            existing_match.ml_prediction_error = (
                ml_prediction_error
            )

            self.db.commit()
            self.db.refresh(
                existing_match,
            )

            return existing_match

        match = Match(
            resume_id=resume_id,
            job_id=job_id,
            match_score=match_score,
            score_breakdown=score_breakdown,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            algorithm_version=algorithm_version,
            ml_predicted_relevance=(
                ml_predicted_relevance
            ),
            ml_predicted_grade=(
                ml_predicted_grade
            ),
            ml_model_name=(
                ml_model_name
            ),
            ml_model_version=(
                ml_model_version
            ),
            ml_feature_set_identifier=(
                ml_feature_set_identifier
            ),
            ml_prediction_status=(
                ml_prediction_status
            ),
            ml_prediction_error=(
                ml_prediction_error
            ),
        )

        self.db.add(
            match,
        )

        self.db.commit()
        self.db.refresh(
            match,
        )

        return match

    def list_by_resume(
        self,
        resume_id: int,
    ) -> list[Match]:
        return (
            self.db.query(Match)
            .filter(
                Match.resume_id == resume_id,
            )
            .order_by(
                Match.match_score.desc(),
                Match.id.asc(),
            )
            .all()
        )

    def list_shadow_predictions_by_resume(
        self,
        resume_id: int,
    ) -> list[Match]:
        return (
            self.db.query(Match)
            .filter(
                Match.resume_id == resume_id,
                Match.ml_predicted_relevance.isnot(
                    None,
                ),
            )
            .order_by(
                Match.match_score.desc(),
                Match.id.asc(),
            )
            .all()
        )

    def count_ml_prediction_statuses(
        self,
        resume_id: int,
    ) -> dict[str, int]:
        rows = (
            self.db.query(
                Match.ml_prediction_status,
                func.count(Match.id),
            )
            .filter(
                Match.resume_id == resume_id,
            )
            .group_by(
                Match.ml_prediction_status,
            )
            .all()
        )

        return {
            str(prediction_status): int(count)
            for prediction_status, count in rows
            if prediction_status is not None
        }