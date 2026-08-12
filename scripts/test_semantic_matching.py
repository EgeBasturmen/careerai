from src.core.database.session import SessionLocal
from src.domains.embeddings.services.semantic_matching_service import (
    SemanticMatchingService,
)


def main():
    db = SessionLocal()

    try:
        service = SemanticMatchingService(
            db,
        )

        results = service.find_jobs_for_resume(
            resume_id=7,
            limit=5,
        )

        for embedding, similarity in results:
            print(
                embedding.entity_id,
                round(similarity, 4),
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()