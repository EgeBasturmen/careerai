from sqlalchemy.orm import Session

from src.domains.jobs.models.job import Job

from datetime import datetime

class JobRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        title: str,
        company_name: str,
        description: str,
        normalized_title: str,
        normalized_company_name: str,
        normalized_location: str,
        fingerprint: str,
        location: str | None = None,
        remote_type: str | None = None,
        seniority: str | None = None,
        required_skills: list[str] | None = None,
        external_id: str | None=None,

        source: str | None = None,
        source_url: str | None = None,

        
    ) -> Job:
        job = Job(
            title=title,
            company_name=company_name,
            description=description,
            location=location,
            remote_type=remote_type,
            seniority=seniority,
            required_skills=required_skills,
            source=source,
            source_url=source_url,
            external_id=external_id,
            normalized_title=normalized_title,
            normalized_company_name=normalized_company_name,
            normalized_location=normalized_location,
            fingerprint=fingerprint,
        )

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        return job

    def list_all(
        self,
        seniority: str | None = None,
        remote_type: str | None = None,
        location: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Job]:
        query = (
            self.db.query(Job)
            .filter(Job.is_active.is_(True))
        )

        if seniority:
            query = query.filter(
                Job.seniority == seniority,
            )

        if remote_type:
            query = query.filter(
                Job.remote_type == remote_type,
            )

        if location:
            query = query.filter(
                Job.location.ilike(f"%{location}%"),
            )

        return (
            query
            .order_by(Job.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
    def get_by_id(
        self,
        job_id: int,
    ) -> Job | None:
        return (
            self.db.query(Job)
            .filter(Job.id == job_id)
            .first()
    )
    def get_by_fingerprint(
        self,
        fingerprint: str,
    ) -> Job | None:
        return (
            self.db.query(Job)
            .filter(Job.fingerprint == fingerprint)
            .first()
        )
    def update_from_ingestion(
        self,
        job: Job,
        title: str,
        company_name: str,
        description: str,
        location: str | None,
        remote_type: str | None,
        seniority: str | None,
        required_skills: list[str],
        source: str | None,
        source_url: str | None,
        external_id: str | None,
        normalized_title: str,
        normalized_company_name: str,
        normalized_location: str,
        fingerprint: str,
    ) -> Job:
        job.title = title
        job.company_name = company_name
        job.description = description
        job.location = location
        job.remote_type = remote_type
        job.seniority = seniority
        job.required_skills = required_skills
        job.source = source
        job.source_url = source_url
        job.external_id = external_id
        job.normalized_title = normalized_title
        job.normalized_company_name = normalized_company_name
        job.normalized_location = normalized_location
        job.fingerprint = fingerprint

        job.last_seen_at = datetime.utcnow()
        job.is_active = True
        job.deactivated_at = None

        self.db.commit()
        self.db.refresh(job)

        return job
    
    def get_by_source_and_external_id(
        self,
        source: str,
        external_id: str,
    ) -> Job | None:
        return (
            self.db.query(Job)
            .filter(
                Job.source == source,
                Job.external_id == external_id,
            )
            .first()
        )
    def list_by_ids(
        self,
        job_ids: list[int],
        seniority: str | None = None,
        remote_type: str | None = None,
        location: str | None = None,
    ) -> list[Job]:
        if not job_ids:
            return []

        query = self.db.query(Job).filter(
            Job.id.in_(job_ids),
            Job.is_active.is_(True),
        )

        if seniority:
            query = query.filter(
                Job.seniority == seniority,
            )

        if remote_type:
            query = query.filter(
                Job.remote_type == remote_type,
            )

        if location:
            query = query.filter(
                Job.location.ilike(
                    f"%{location}%"
                ),
            )

        jobs = query.all()

        order_map = {
            job_id: index
            for index, job_id in enumerate(job_ids)
        }

        return sorted(
            jobs,
            key=lambda job: order_map.get(
                job.id,
                len(job_ids),
            ),
        )

    def deactivate_stale_jobs(
        self,
        *,
        stale_before: datetime,
    ) -> int:
        deactivated_at = datetime.utcnow()

        affected_count = (
            self.db.query(Job)
            .filter(
                Job.is_active.is_(True),
                Job.last_seen_at < stale_before,
            )
            .update(
                {
                    Job.is_active: False,
                    Job.deactivated_at: (
                        deactivated_at
                    ),
                },
                synchronize_session=False,
            )
        )

        self.db.commit()

        return affected_count