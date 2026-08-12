from sqlalchemy.orm import Session

from src.domains.matching.models.match import Match
from src.domains.matching.models.match_feedback import (
    MatchFeedback,
)


class MatchTrainingRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def list_labeled_matches(
        self,
        algorithm_version: str | None = None,
    ) -> list[tuple[Match, MatchFeedback]]:
        query = (
            self.db.query(
                Match,
                MatchFeedback,
            )
            .join(
                MatchFeedback,
                (
                    MatchFeedback.resume_id
                    == Match.resume_id
                )
                & (
                    MatchFeedback.job_id
                    == Match.job_id
                ),
            )
        )

        if algorithm_version:
            query = query.filter(
                Match.algorithm_version
                == algorithm_version,
            )

        return (
            query
            .order_by(
                MatchFeedback.resume_id.asc(),
                MatchFeedback.job_id.asc(),
            )
            .all()
        )