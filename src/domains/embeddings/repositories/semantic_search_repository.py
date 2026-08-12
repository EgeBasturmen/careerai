from sqlalchemy.orm import Session

from src.domains.embeddings.models.entity_embedding import (
    EntityEmbedding,
)
from src.domains.jobs.models.job import Job


class SemanticSearchRepository:
    JOB_ENTITY_TYPE = "job"

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def find_similar_jobs(
        self,
        query_vector: list[float],
        model_name: str,
        limit: int = 10,
        minimum_similarity: float | None = None,
    ) -> list[tuple[Job, float]]:
        distance_expression = (
            EntityEmbedding.embedding.cosine_distance(
                query_vector,
            )
        )

        query = (
            self.db.query(
                Job,
                distance_expression.label("distance"),
            )
            .join(
                EntityEmbedding,
                (
                    EntityEmbedding.entity_id == Job.id
                )
                &
                (
                    EntityEmbedding.entity_type
                    == self.JOB_ENTITY_TYPE
                ),
            )
            .filter(
                EntityEmbedding.model_name
                == model_name,
                Job.is_active == True,
            )
        )

        if minimum_similarity is not None:
            query = query.filter(
                distance_expression
                <= 1.0 - minimum_similarity,
            )

        rows = (
            query
            .order_by(distance_expression.asc())
            .limit(limit)
            .all()
        )

        return [
            (
                job,
                1.0 - float(distance),
            )
            for job, distance in rows
        ]

    def get_job_similarities(
        self,
        query_vector: list[float],
        job_ids: list[int],
        model_name: str,
    ) -> dict[int, float]:
        if not job_ids:
            return {}

        distance_expression = (
            EntityEmbedding.embedding.cosine_distance(
                query_vector,
            )
        )

        rows = (
            self.db.query(
                EntityEmbedding.entity_id,
                distance_expression.label("distance"),
            )
            .join(
                Job,
                Job.id == EntityEmbedding.entity_id,
            )
            .filter(
                EntityEmbedding.entity_type
                == self.JOB_ENTITY_TYPE,
                EntityEmbedding.entity_id.in_(job_ids),
                EntityEmbedding.model_name
                == model_name,
                Job.is_active.is_(True),
            )
            .all()
        )
        return {
            entity_id: 1.0 - float(distance)
            for entity_id, distance in rows
            if distance is not None
        }
    def find_similar_job_ids(
        self,
        query_vector: list[float],
        model_name: str,
        candidate_limit: int = 100,
        minimum_similarity: float | None = None,
    ) -> list[tuple[int, float]]:
        distance_expression = (
            EntityEmbedding.embedding.cosine_distance(
                query_vector,
            )
        )

        query = (
            self.db.query(
                EntityEmbedding.entity_id,
                distance_expression.label(
                    "distance",
                ),
            )
            .join(
                Job,
                Job.id == EntityEmbedding.entity_id,
            )
            .filter(
                EntityEmbedding.entity_type
                == self.JOB_ENTITY_TYPE,
                EntityEmbedding.model_name
                == model_name,
                Job.is_active.is_(True),
            )
        )

        if minimum_similarity is not None:
            query = query.filter(
                distance_expression
                <= 1.0 - minimum_similarity,
            )

        rows = (
            query
            .order_by(
                distance_expression.asc(),
            )
            .limit(candidate_limit)
            .all()
        )

        return [
            (
                int(entity_id),
                1.0 - float(distance),
            )
            for entity_id, distance in rows
            if distance is not None
        ]