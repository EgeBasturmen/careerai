from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domains.knowledge.models.rag_answer_evaluation import (
    RAGAnswerEvaluation,
)


class RAGAnswerEvaluationRepository:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def add(
        self,
        evaluation: RAGAnswerEvaluation,
    ) -> RAGAnswerEvaluation:
        self.db.add(evaluation)
        self.db.flush()

        return evaluation

    def get_by_id(
        self,
        evaluation_id: int,
    ) -> RAGAnswerEvaluation | None:
        statement = select(
            RAGAnswerEvaluation
        ).where(
            RAGAnswerEvaluation.id
            == evaluation_id
        )

        return self.db.scalar(statement)

    def list_by_rag_run_id(
        self,
        rag_run_id: int,
    ) -> list[RAGAnswerEvaluation]:
        statement = (
            select(RAGAnswerEvaluation)
            .where(
                RAGAnswerEvaluation.rag_run_id
                == rag_run_id
            )
            .order_by(
                RAGAnswerEvaluation.created_at.desc(),
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_by_run_profile_and_version(
        self,
        *,
        rag_run_id: int,
        evaluation_profile: str,
        evaluator_version: str,
    ) -> RAGAnswerEvaluation | None:
        statement = (
            select(RAGAnswerEvaluation)
            .where(
                RAGAnswerEvaluation.rag_run_id
                == rag_run_id,
                RAGAnswerEvaluation
                .evaluation_profile
                == evaluation_profile,
                RAGAnswerEvaluation
                .evaluator_version
                == evaluator_version,
            )
            .order_by(
                RAGAnswerEvaluation
                .created_at
                .desc()
            )
            .limit(1)
        )

        return self.db.scalar(statement)