import src.core.database.models  # noqa

from src.core.database.session import SessionLocal
from src.domains.resumes.repositories.resume_repository import (
    ResumeRepository,
)
from src.domains.resumes.services.pdf_text_extractor import (
    PDFTextExtractor,
)
from src.infrastructure.queue.celery_app import celery_app
from src.shared.enums.resume_status import ResumeStatus
from src.domains.resumes.services.resume_parser import ResumeParser
from src.domains.embeddings.services.resume_embedding_service import (
    ResumeEmbeddingService,
)

@celery_app.task
def process_resume(
    resume_id: int,
):
    db = SessionLocal()

    try:
        repository = ResumeRepository(db)

        resume = repository.get_by_id(
            resume_id,
        )

        if resume is None:
            print(
                f"Resume {resume_id} not found"
            )
            return

        repository.update_status(
            resume=resume,
            status=ResumeStatus.PROCESSING,
        )

        extractor = PDFTextExtractor()

        raw_text = extractor.extract_text(
            resume.storage_path,
        )
        parser = ResumeParser()

        parsed_profile = parser.parse(
            raw_text,
        )       

        repository.update_raw_text(
            resume=resume,
            raw_text=raw_text,
        )
        repository.update_parsed_profile(
            resume=resume,
            parsed_profile=parsed_profile,
        )
        resume_embedding_service = ResumeEmbeddingService(
            db,
        )

        resume_embedding_service.generate_and_save(
            resume,
        )

        repository.update_status(
            resume=resume,
            status=ResumeStatus.COMPLETED,
        )

        print(
            f"Resume {resume_id} completed. Extracted {len(raw_text)} characters."
        )

    except Exception as exc:
        print(
            f"Resume {resume_id} failed: {exc}"
        )

        db.rollback()

        if "repository" in locals() and "resume" in locals() and resume:
            repository.update_status(
                resume=resume,
                status=ResumeStatus.FAILED,
            )

        raise

    finally:
        db.close()