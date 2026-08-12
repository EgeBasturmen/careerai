from sqlalchemy.orm import Session

from src.domains.resumes.models.resume import Resume




class ResumeRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def get_by_id(
        self,
        resume_id: int,
    ) -> Resume | None:
        return (
            self.db.query(Resume)
            .filter(Resume.id == resume_id)
            .first()
        )

    def create(
        self,
        *,
        user_id: int,
        original_filename: str,
        storage_path: str,
        file_hash: str | None = None,
        source: str = "user_upload",
        dataset_name: str | None = None,
        dataset_category: str | None = None,
    ) -> Resume:
        resume = Resume(
            user_id=user_id,
            original_filename=original_filename,
            storage_path=storage_path,
            file_hash=file_hash,
            source=source,
            dataset_name=dataset_name,
            dataset_category=dataset_category,
        )

        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)

        return resume

    def update_status(
        self,
        resume: Resume,
        status: str,
    ) -> Resume:
        resume.status = status

        self.db.commit()
        self.db.refresh(resume)

        return resume
    
    def get_by_id_and_user(
        self,
        resume_id: int,
        user_id: int,
    ) -> Resume | None:
        return (
            self.db.query(Resume)
            .filter(
                Resume.id == resume_id,
                Resume.user_id == user_id,
            )
            .first()
        )
    
    def update_raw_text(
        self,
        resume: Resume,
        raw_text: str,
    ) -> Resume:
        resume.raw_text = raw_text

        self.db.commit()
        self.db.refresh(resume)

        return resume

    def update_parsed_profile(
        self,
        resume: Resume,
        parsed_profile: dict,
    ) -> Resume:
        resume.parsed_profile = parsed_profile

        self.db.commit()
        self.db.refresh(resume)

        return resume


    def get_by_file_hash(
        self,
        *,
        file_hash: str,
        dataset_name: str | None = None,
    ) -> Resume | None:
        query = self.db.query(
            Resume
        ).filter(
            Resume.file_hash == file_hash,
        )

        if dataset_name is not None:
            query = query.filter(
                Resume.dataset_name
                == dataset_name,
            )

        return query.first()


    def list_by_dataset(
        self,
        *,
        dataset_name: str,
        dataset_category: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Resume]:
        query = (
            self.db.query(Resume)
            .filter(
                Resume.dataset_name
                == dataset_name,
            )
        )

        if dataset_category is not None:
            query = query.filter(
                Resume.dataset_category
                == dataset_category,
            )

        return (
            query
            .order_by(
                Resume.id.asc(),
            )
            .offset(offset)
            .limit(limit)
            .all()
        )
    

