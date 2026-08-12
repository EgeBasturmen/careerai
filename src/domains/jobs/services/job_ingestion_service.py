from sqlalchemy.orm import Session

from src.domains.embeddings.services.job_embedding_service import (
    JobEmbeddingService,
)
from src.domains.jobs.repositories.job_repository import (
    JobRepository,
)
from src.domains.jobs.schemas.job_ingestion_schema import (
    JobIngestionResult,
)
from src.domains.jobs.services.job_fingerprint_service import (
    JobFingerprintService,
)
from src.domains.jobs.services.job_normalizer import (
    JobNormalizer,
)
from src.domains.jobs.services.job_parser import (
    JobParser,
)
from src.infrastructure.job_sources.base import (
    ExternalJob,
    JobSourceClient,
)

from src.domains.embeddings.schemas.embedding_generation_schema import (
    EmbeddingGenerationStatus,
)
from src.domains.jobs.schemas.job_ingestion_schema import (
    JobIngestionResult,
    SingleJobIngestionResult,
)

class JobIngestionService:
    def __init__(
        self,
        db: Session,
    ):
        self.repository = JobRepository(db)
        self.job_parser = JobParser()
        self.normalizer = JobNormalizer()
        self.fingerprint_service = (
            JobFingerprintService()
        )
        self.job_embedding_service = (
            JobEmbeddingService(
                db,
            )
        )

    def ingest(
        self,
        source_client: JobSourceClient,
    ) -> JobIngestionResult:
        external_jobs = (
            source_client.fetch_jobs()
        )

        created_count = 0
        updated_count = 0
        failed_count = 0

        embedding_created_count = 0
        embedding_updated_count = 0
        embedding_skipped_count = 0

        errors: list[str] = []

        for external_job in external_jobs:
            try:
                ingestion_result = (
                    self._ingest_single_job(
                        external_job=external_job,
                        source_name=(
                            source_client.source_name
                        ),
                    )
                )

                if ingestion_result.was_created:
                    created_count += 1
                else:
                    updated_count += 1

                if (
                    ingestion_result.embedding_status
                    == EmbeddingGenerationStatus.CREATED
                ):
                    embedding_created_count += 1

                elif (
                    ingestion_result.embedding_status
                    == EmbeddingGenerationStatus.UPDATED
                ):
                    embedding_updated_count += 1

                elif (
                    ingestion_result.embedding_status
                    == EmbeddingGenerationStatus.SKIPPED
                ):
                    embedding_skipped_count += 1

            except Exception as exc:
                failed_count += 1

                errors.append(
                    (
                        "external_id="
                        f"{external_job.external_id}: "
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    )
                )

        return JobIngestionResult(
            source=source_client.source_name,
            fetched_count=len(external_jobs),
            created_count=created_count,
            updated_count=updated_count,
            failed_count=failed_count,
            embedding_created_count=(
                embedding_created_count
            ),
            embedding_updated_count=(
                embedding_updated_count
            ),
            embedding_skipped_count=(
                embedding_skipped_count
            ),
            errors=errors,
        )


    def _ingest_single_job(
        self,
        external_job: ExternalJob,
        source_name: str,
    ) -> SingleJobIngestionResult:
        parsed_job = self.job_parser.parse(
            external_job.description,
        )

        required_skills = parsed_job[
            "required_skills"
        ]

        seniority = (
            external_job.seniority
            or parsed_job["seniority"]
        )

        remote_type = (
            external_job.remote_type
            or parsed_job["remote_type"]
        )

        normalized_title = (
            self.normalizer.normalize_title(
                external_job.title,
            )
        )

        normalized_company_name = (
            self.normalizer
            .normalize_company_name(
                external_job.company_name,
            )
        )

        normalized_location = (
            self.normalizer.normalize_location(
                external_job.location,
            )
        )

        fingerprint = (
            self.fingerprint_service.generate(
                title=external_job.title,
                company_name=(
                    external_job.company_name
                ),
                location=external_job.location,
                description=(
                    external_job.description
                ),
            )
        )

        existing_job = (
            self.repository
            .get_by_source_and_external_id(
                source=source_name,
                external_id=(
                    external_job.external_id
                ),
            )
        )

        if existing_job is None:
            existing_job = (
                self.repository
                .get_by_fingerprint(
                    fingerprint,
                )
            )

        if existing_job is not None:
            updated_job = (
                self.repository
                .update_from_ingestion(
                    job=existing_job,
                    title=external_job.title,
                    company_name=(
                        external_job.company_name
                    ),
                    description=(
                        external_job.description
                    ),
                    location=(
                        external_job.location
                    ),
                    remote_type=remote_type,
                    seniority=seniority,
                    required_skills=(
                        required_skills
                    ),
                    source=source_name,
                    source_url=(
                        external_job.source_url
                    ),
                    external_id=(
                        external_job.external_id
                    ),
                    normalized_title=(
                        normalized_title
                    ),
                    normalized_company_name=(
                        normalized_company_name
                    ),
                    normalized_location=(
                        normalized_location
                    ),
                    fingerprint=fingerprint,
                )
            )

            embedding_result = (
                self.job_embedding_service
                .generate_and_save(
                    updated_job,
                )
            )

            return SingleJobIngestionResult(
                was_created=False,
                embedding_status=(
                    embedding_result.status
                ),
            )

        created_job = self.repository.create(
            title=external_job.title,
            company_name=(
                external_job.company_name
            ),
            description=(
                external_job.description
            ),
            location=external_job.location,
            remote_type=remote_type,
            seniority=seniority,
            required_skills=required_skills,
            source=source_name,
            source_url=(
                external_job.source_url
            ),
            external_id=(
                external_job.external_id
            ),
            normalized_title=(
                normalized_title
            ),
            normalized_company_name=(
                normalized_company_name
            ),
            normalized_location=(
                normalized_location
            ),
            fingerprint=fingerprint,
        )

        self.job_embedding_service\
            .generate_and_save(
                created_job,
            )

        return True