import hashlib

from sqlalchemy.orm import Session

from src.domains.embeddings.builders.job_text_builder import (
    JobTextBuilder,
)
from src.domains.embeddings.clients.factory import (
    get_embedding_client,
)
from src.domains.embeddings.repositories.entity_embedding_repository import (
    EntityEmbeddingRepository,
)
from src.domains.embeddings.schemas.embedding_generation_schema import (
    EmbeddingGenerationResult,
    EmbeddingGenerationStatus,
)
from src.domains.embeddings.services.embedding_service import (
    EmbeddingService,
)
from src.domains.jobs.models.job import Job


class JobEmbeddingService:
    ENTITY_TYPE = "job"

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.text_builder = JobTextBuilder()

        self.embedding_client = (
            get_embedding_client()
        )

        self.embedding_service = EmbeddingService(
            client=self.embedding_client,
        )

        self.repository = (
            EntityEmbeddingRepository(
                db,
            )
        )

    def generate_and_save(
        self,
        job: Job,
    ) -> EmbeddingGenerationResult:
        source_text = self.text_builder.build(
            job,
        )

        if not source_text:
            raise ValueError(
                "Job embedding text is empty"
            )

        source_text_hash = (
            self._build_source_text_hash(
                source_text,
            )
        )

        model_name = (
            self.embedding_client.model_name
        )

        existing_embedding = (
            self.repository
            .get_by_entity_and_model(
                entity_type=self.ENTITY_TYPE,
                entity_id=job.id,
                model_name=model_name,
            )
        )

        if existing_embedding is not None:
            if (
                existing_embedding.source_text_hash
                == source_text_hash
            ):
                return EmbeddingGenerationResult(
                    status=(
                        EmbeddingGenerationStatus
                        .SKIPPED
                    ),
                    entity_type=self.ENTITY_TYPE,
                    entity_id=job.id,
                    model_name=model_name,
                    reason="CONTENT_UNCHANGED",
                )

            # Eski kayıtların hash alanı null olabilir.
            # Metin zaten aynıysa embedding üretmeden
            # yalnızca hash alanını dolduruyoruz.
            if (
                existing_embedding.source_text_hash
                is None
                and existing_embedding.source_text
                == source_text
            ):
                self.repository\
                    .update_source_text_hash(
                        entity_embedding=(
                            existing_embedding
                        ),
                        source_text_hash=(
                            source_text_hash
                        ),
                    )

                return EmbeddingGenerationResult(
                    status=(
                        EmbeddingGenerationStatus
                        .SKIPPED
                    ),
                    entity_type=self.ENTITY_TYPE,
                    entity_id=job.id,
                    model_name=model_name,
                    reason="HASH_BACKFILLED",
                )

        embedding_result = (
            self.embedding_service.embed_text(
                source_text,
            )
        )

        self.repository.upsert(
            entity_type=self.ENTITY_TYPE,
            entity_id=job.id,
            provider=embedding_result.provider,
            model_name=embedding_result.model,
            dimension=embedding_result.dimension,
            source_text=source_text,
            source_text_hash=source_text_hash,
            embedding=embedding_result.vector,
        )

        status = (
            EmbeddingGenerationStatus.CREATED
            if existing_embedding is None
            else EmbeddingGenerationStatus.UPDATED
        )

        return EmbeddingGenerationResult(
            status=status,
            entity_type=self.ENTITY_TYPE,
            entity_id=job.id,
            model_name=embedding_result.model,
        )

    @staticmethod
    def _build_source_text_hash(
        source_text: str,
    ) -> str:
        return hashlib.sha256(
            source_text.encode("utf-8")
        ).hexdigest()