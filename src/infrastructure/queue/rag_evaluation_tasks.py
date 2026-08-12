from typing import Any

import src.core.database.models  # noqa: F401

from src.core.database.session import SessionLocal
from src.domains.knowledge.evaluation.answer.factory import (
    create_answer_evaluation_service,
)
from src.domains.knowledge.rag.rag_context import (
    RAGContext,
    RAGContextItem,
)
from src.domains.knowledge.rag.rag_generation_result import (
    RAGGeneratedCitation,
    RAGGenerationResult,
)
from src.domains.knowledge.rag.rag_source_validator import (
    RAGSourceValidator,
)
from src.domains.knowledge.repositories.rag_answer_evaluation_repository import (
    RAGAnswerEvaluationRepository,
)
from src.domains.knowledge.repositories.rag_run_repository import (
    RAGRunRepository,
)
from src.domains.knowledge.services.rag_answer_evaluation_persistence_service import (
    RAGAnswerEvaluationPersistenceService,
)
from src.infrastructure.llm.llm_factory import (
    get_llm_client,
)
from src.infrastructure.queue.celery_app import (
    celery_app,
)


EVALUATION_PROFILE = "default"
EVALUATOR_VERSION = "v1"


def _metadata_string(
    metadata: dict[str, Any],
    key: str,
    default: str,
) -> str:
    value = metadata.get(key)

    if value is None:
        return default

    normalized_value = str(value).strip()

    return normalized_value or default


def _metadata_optional_string(
    metadata: dict[str, Any],
    key: str,
) -> str | None:
    value = metadata.get(key)

    if value is None:
        return None

    normalized_value = str(value).strip()

    return normalized_value or None


def _build_rag_context(
    rag_run,
) -> RAGContext:
    included_chunks = [
        chunk
        for chunk in rag_run.chunks
        if chunk.was_included_in_context
    ]

    included_chunks.sort(
        key=lambda chunk: chunk.source_number
    )

    items = tuple(
        RAGContextItem(
            source_number=chunk.source_number,
            chunk_id=chunk.knowledge_chunk_id,
            document_id=(
                chunk.knowledge_document_id
            ),
            document_title=(
                chunk.document_title
            ),
            content=chunk.chunk_content,
            similarity_score=(
                chunk.similarity_score
            ),
            chunk_index=chunk.chunk_index,
            source_type=_metadata_string(
                chunk.chunk_metadata or {},
                "source_type",
                "unknown",
            ),
            source_uri=_metadata_optional_string(
                chunk.chunk_metadata or {},
                "source_uri",
            ),
            category=_metadata_optional_string(
                chunk.chunk_metadata or {},
                "category",
            ),
            language=_metadata_string(
                chunk.chunk_metadata or {},
                "language",
                rag_run.language or "unknown",
            ),
        )
        for chunk in included_chunks
    )

    context_text = "\n\n".join(
        (
            f"[Source {item.source_number}]\n"
            f"Title: {item.document_title}\n"
            f"{item.content}"
        )
        for item in items
    )

    return RAGContext(
        text=context_text,
        items=items,
        source_count=len(items),
        character_count=len(context_text),
    )


def _build_generation_result(
    rag_run,
) -> RAGGenerationResult:
    citations = tuple(
        RAGGeneratedCitation(
            source_number=int(
                citation["source_number"]
            ),
            claim=str(
                citation.get(
                    "claim",
                    "",
                )
            ),
        )
        for citation in (rag_run.citations or [])
        if citation.get("source_number")
        is not None
    )

    answer = rag_run.answer or ""

    return RAGGenerationResult(
        answer=answer,
        citations=citations,
        sufficient_context=bool(
            rag_run.sufficient_context
        ),
        confidence=float(
            rag_run.confidence or 0.0
        ),
        raw_response=answer,
    )


@celery_app.task(
    bind=True,
    name="knowledge.evaluate_rag_answer",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={
        "max_retries": 3,
    },
)
def evaluate_rag_answer_task(
    self,
    rag_run_id: int,
) -> dict[str, Any]:
    db = SessionLocal()

    try:
        rag_run_repository = (
            RAGRunRepository(db)
        )

        evaluation_repository = (
            RAGAnswerEvaluationRepository(db)
        )

        existing_evaluation = (
            evaluation_repository
            .get_by_run_profile_and_version(
                rag_run_id=rag_run_id,
                evaluation_profile=(
                    EVALUATION_PROFILE
                ),
                evaluator_version=(
                    EVALUATOR_VERSION
                ),
            )
        )

        if existing_evaluation is not None:
            return {
                "evaluation_id": (
                    existing_evaluation.id
                ),
                "rag_run_id": rag_run_id,
                "status": "ALREADY_EVALUATED",
                "overall_score": (
                    existing_evaluation
                    .overall_score
                ),
                "passed": (
                    existing_evaluation.passed
                ),
            }

        rag_run = (
            rag_run_repository
            .get_by_id_for_evaluation(
                rag_run_id=rag_run_id,
            )
        )

        if rag_run is None:
            raise ValueError(
                "RAG run not found: "
                f"{rag_run_id}"
            )

        if rag_run.generation_status not in {
            "SUCCESS",
            "NO_CONTEXT",
        }:
            raise ValueError(
                "RAG run is not ready for "
                "evaluation. "
                f"Current status: "
                f"{rag_run.generation_status}"
            )

        if not rag_run.answer:
            raise ValueError(
                "RAG run has no generated "
                "answer to evaluate"
            )

        rag_context = _build_rag_context(
            rag_run
        )

        generation_result = (
            _build_generation_result(
                rag_run
            )
        )

        source_validation_result = (
            RAGSourceValidator().validate(
                generation_result=(
                    generation_result
                ),
                context=rag_context,
            )
        )

        llm_client = get_llm_client()

        evaluation_service = (
            create_answer_evaluation_service(
                llm_client=llm_client,
            )
        )

        report = evaluation_service.evaluate(
            question=rag_run.question,
            generation_result=(
                generation_result
            ),
            rag_context=rag_context,
            source_validation_result=(
                source_validation_result
            ),
        )

        persistence_service = (
            RAGAnswerEvaluationPersistenceService(
                db=db,
            )
        )

        saved_evaluation = (
            persistence_service.save(
                rag_run_id=rag_run.id,
                report=report,
                evaluation_profile=(
                    EVALUATION_PROFILE
                ),
                evaluator_version=(
                    EVALUATOR_VERSION
                ),
                judge_provider=(
                    llm_client.provider_name
                ),
                judge_model=(
                    llm_client.model_name
                ),
            )
        )

        return {
            "evaluation_id": (
                saved_evaluation.id
            ),
            "rag_run_id": rag_run.id,
            "status": "COMPLETED",
            "overall_score": (
                saved_evaluation.overall_score
            ),
            "passed": (
                saved_evaluation.passed
            ),
            "evaluator_count": (
                saved_evaluation.evaluator_count
            ),
            "failed_evaluator_names": (
                saved_evaluation
                .failed_evaluator_names
            ),
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()