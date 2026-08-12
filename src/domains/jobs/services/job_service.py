from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.domains.embeddings.services.job_embedding_service import (
    JobEmbeddingService,
)
from src.domains.jobs.repositories.job_repository import (
    JobRepository,
)
from src.domains.jobs.schemas.job_schema import (
    JobCreateRequest,
    JobResponse,
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


class JobService:
    def __init__(
        self,
        db: Session,
    ):
        self.repository = JobRepository(db)
        self.job_parser = JobParser()
        self.normalizer = JobNormalizer()
        self.fingerprint_service = JobFingerprintService()

        self.job_embedding_service = JobEmbeddingService(
            db,
        )

    def create_job(
        self,
        request: JobCreateRequest,
    ) -> JobResponse:
        parsed_job = self.job_parser.parse(
            request.description,
        )

        required_skills = (
            request.required_skills
            or parsed_job["required_skills"]
        )

        seniority = (
            request.seniority
            or parsed_job["seniority"]
        )

        remote_type = (
            request.remote_type
            or parsed_job["remote_type"]
        )

        normalized_title = (
            self.normalizer.normalize_title(
                request.title,
            )
        )

        normalized_company_name = (
            self.normalizer.normalize_company_name(
                request.company_name,
            )
        )

        normalized_location = (
            self.normalizer.normalize_location(
                request.location,
            )
        )

        fingerprint = (
            self.fingerprint_service.generate(
                title=request.title,
                company_name=request.company_name,
                location=request.location,
                description=request.description,
            )
        )

        existing_job = (
            self.repository.get_by_fingerprint(
                fingerprint,
            )
        )

        if existing_job is not None:
            updated_job = (
                self.repository.update_from_ingestion(
                    job=existing_job,
                    title=request.title,
                    company_name=request.company_name,
                    description=request.description,
                    location=request.location,
                    remote_type=remote_type,
                    seniority=seniority,
                    required_skills=required_skills,
                    source=request.source,
                    source_url=request.source_url,
                    external_id=request.external_id,
                    normalized_title=normalized_title,
                    normalized_company_name=(
                        normalized_company_name
                    ),
                    normalized_location=(
                        normalized_location
                    ),
                    fingerprint=fingerprint,
                )
            )

            self.job_embedding_service.generate_and_save(
                updated_job,
            )

            return JobResponse.model_validate(
                updated_job,
            )

        job = self.repository.create(
            title=request.title,
            company_name=request.company_name,
            description=request.description,
            location=request.location,
            remote_type=remote_type,
            seniority=seniority,
            required_skills=required_skills,
            source=request.source,
            source_url=request.source_url,
            external_id=request.external_id,
            normalized_title=normalized_title,
            normalized_company_name=(
                normalized_company_name
            ),
            normalized_location=(
                normalized_location
            ),
            fingerprint=fingerprint,
        )

        self.job_embedding_service.generate_and_save(
            job,
        )

        return JobResponse.model_validate(
            job,
        )

    def get_job(
        self,
        job_id: int,
    ) -> JobResponse:
        job = self.repository.get_by_id(
            job_id,
        )

        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

        return JobResponse.model_validate(
            job,
        )

    def list_jobs(
        self,
        seniority: str | None = None,
        remote_type: str | None = None,
        location: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[JobResponse]:
        jobs = self.repository.list_all(
            seniority=seniority,
            remote_type=remote_type,
            location=location,
            limit=limit,
            offset=offset,
        )

        return [
            JobResponse.model_validate(job)
            for job in jobs
        ]