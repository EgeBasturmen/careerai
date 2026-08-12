from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from src.domains.knowledge.repositories.rag_run_repository import (
    RAGRunRepository,
)
from src.domains.knowledge.schemas.rag_run_schema import (
    RAGRunDetailResponse,
    RAGRunChunkResponse,
    RAGRunListItemResponse,
    RAGRunListResponse,
)


class RAGRunQueryService:
    ALLOWED_STATUSES = {
        "PROCESSING",
        "SUCCESS",
        "NO_CONTEXT",
        "INVALID_GENERATION",
        "FAILED",
    }

    def __init__(
        self,
        db: Session,
    ):
        self.repository = (
            RAGRunRepository(
                db,
            )
        )

    def list_runs(
        self,
        *,
        user_id: int,
        limit: int,
        offset: int,
        generation_status: str | None,
    ) -> RAGRunListResponse:
        normalized_status = (
            self._normalize_status(
                generation_status
            )
        )

        runs = (
            self.repository.list_by_user(
                user_id=user_id,
                limit=limit,
                offset=offset,
                generation_status=(
                    normalized_status
                ),
            )
        )

        total = (
            self.repository.count_by_user(
                user_id=user_id,
                generation_status=(
                    normalized_status
                ),
            )
        )

        items = [
            RAGRunListItemResponse
            .model_validate(
                rag_run
            )
            for rag_run in runs
        ]

        return RAGRunListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )

    def get_run_detail(
        self,
        *,
        rag_run_id: int,
        user_id: int,
    ) -> RAGRunDetailResponse:
        rag_run = (
            self.repository
            .get_detail_by_id(
                rag_run_id=rag_run_id,
                user_id=user_id,
            )
        )

        if rag_run is None:
            raise HTTPException(
                status_code=(
                    status
                    .HTTP_404_NOT_FOUND
                ),
                detail=(
                    "RAG run not found"
                ),
            )

        ordered_chunks = sorted(
            rag_run.chunks,
            key=lambda chunk: (
                chunk.retrieval_rank,
                chunk.source_number,
            ),
        )

        response = (
            RAGRunDetailResponse
            .model_validate(
                rag_run
            )
        )

        chunk_responses = [
            RAGRunChunkResponse
            .model_validate(
                chunk
            )
            for chunk in ordered_chunks
        ]

        return response.model_copy(
            update={
                "chunks": chunk_responses,
            }
        )

    def _normalize_status(
        self,
        generation_status: str | None,
    ) -> str | None:
        if generation_status is None:
            return None

        normalized_status = (
            generation_status
            .strip()
            .upper()
        )

        if (
            normalized_status
            not in self.ALLOWED_STATUSES
        ):
            allowed_statuses = ", ".join(
                sorted(
                    self.ALLOWED_STATUSES
                )
            )

            raise HTTPException(
                status_code=(
                    status
                    .HTTP_422_UNPROCESSABLE_ENTITY
                ),
                detail=(
                    "Invalid generation status. "
                    "Allowed values: "
                    f"{allowed_statuses}"
                ),
            )

        return normalized_status