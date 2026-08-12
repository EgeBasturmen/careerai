from sqlalchemy.orm import Session

from src.domains.cv_improvement.models.cv_improvement import (
    CVImprovement,
)


class CVImprovementRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def get_by_resume_and_job(
            
            self,
            resume_id:int,
            job_id:int,
            language:str

    )->CVImprovement | None:
        return(
            self.db.query(CVImprovement)
            .filter(
                CVImprovement.resume_id==resume_id,
                CVImprovement.job_id==job_id,
                CVImprovement.language==language,
            )
            .first()
        )
    def create(
            self,
            resume_id:int,
            job_id:int,
            result:dict,
            language:str,
            
    )->CVImprovement:
        improvement= CVImprovement(
            resume_id=resume_id,
            job_id=job_id,
            language=language,
            result=result,
        )
        self.db.add(improvement)
        self.db.commit()
        self.db.refresh(improvement)
        return improvement
    
    def update(
        self,
        improvement: CVImprovement,
        result: dict,
        
    ) -> CVImprovement:
        improvement.result = result

        self.db.commit()
        self.db.refresh(improvement)

        return improvement

    def upsert(
        self,
        resume_id: int,
        job_id: int,
        result: dict,
        language:str,
    ) -> CVImprovement:
        existing_improvement = self.get_by_resume_and_job(
            resume_id=resume_id,
            job_id=job_id,
            language=language,
        )

        if existing_improvement:
            return self.update(
                improvement=existing_improvement,
                result=result,
            )

        return self.create(
            resume_id=resume_id,
            job_id=job_id,
            result=result,
            language=language,
        )

    def list_by_resume(
        self,
        resume_id: int,
        language: str | None = None,
    ) -> list[CVImprovement]:
        query = self.db.query(CVImprovement).filter(
            CVImprovement.resume_id == resume_id,
        )

        if language:
            query = query.filter(
                CVImprovement.language == language,
            )

        return (
            query
            .order_by(CVImprovement.created_at.desc())
            .all()
        )