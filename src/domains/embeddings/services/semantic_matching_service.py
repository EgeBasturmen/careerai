from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.domains.embeddings.clients.factory import (
    get_embedding_client,
)
from src.domains.embeddings.repositories.entity_embedding_repository import (
    EntityEmbeddingRepository,
)
from src.domains.embeddings.repositories.semantic_search_repository import (
    SemanticSearchRepository,
)
from src.domains.embeddings.schemas.semantic_search_schema import (
    SemanticJobMatchResponse,
)
from src.domains.resumes.repositories.resume_repository import (
    ResumeRepository,
)
from src.domains.users.models.user import User


class SemanticMatchingService:
    RESUME_ENTITY_TYPE = "resume"

    def __init__(
        self,
        db: Session,
    ):
        self.resume_repository = ResumeRepository(
            db,
        )

        self.embedding_repository = (
            EntityEmbeddingRepository(db)
        )

        self.semantic_search_repository = (
            SemanticSearchRepository(db)
        )

        self.embedding_client = (
            get_embedding_client()
        )

    def find_jobs_for_resume(
        self,
        current_user: User,
        resume_id: int,
        limit: int = 10,
        minimum_similarity: float | None = None,
    ) -> list[SemanticJobMatchResponse]:
        resume = (
            self.resume_repository.get_by_id_and_user(
                resume_id=resume_id,
                user_id=current_user.id,
            )
        )

        if resume is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

        resume_embedding = (
            self.embedding_repository.get_by_entity_and_model(
                entity_type=self.RESUME_ENTITY_TYPE,
                entity_id=resume.id,
                model_name=self.embedding_client.model_name,
            )
        )

        if resume_embedding is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Resume embedding has not been "
                    "generated yet"
                ),
            )

        if (
            resume_embedding.dimension
            != self.embedding_client.embedding_dimension
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Resume embedding dimension does "
                    "not match the active model"
                ),
            )

        rows = (
            self.semantic_search_repository.find_similar_jobs(
                query_vector=list(
                    resume_embedding.embedding,
                ),
                model_name=self.embedding_client.model_name,
                limit=limit,
                minimum_similarity=minimum_similarity,
            )
        )

        return [
            SemanticJobMatchResponse(
                job_id=job.id,
                title=job.title,
                company_name=job.company_name,
                location=job.location,
                remote_type=job.remote_type,
                seniority=job.seniority,
                required_skills=(
                    job.required_skills or []
                ),
                similarity_score=round(
                    similarity,
                    4,
                ),
            )
            for job, similarity in rows
        ]