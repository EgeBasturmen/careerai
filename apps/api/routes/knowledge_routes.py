from fastapi import (
    APIRouter,
    Depends,
    Query,
    Response,
    status,
)
from sqlalchemy.orm import Session

from src.core.database.session import get_db
from src.core.security.dependencies import (
    get_current_user,
)
from src.domains.knowledge.schemas.knowledge_schema import (
    KnowledgeDocumentCreateRequest,
    KnowledgeDocumentDetailResponse,
    KnowledgeDocumentResponse,
)
from src.domains.knowledge.services.knowledge_service import (
    KnowledgeService,
)
from src.domains.users.models.user import User
from src.domains.knowledge.schemas.knowledge_retrieval_schema import (
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
)
from src.domains.knowledge.services.knowledge_retriever import (
    KnowledgeRetriever,
)
from src.domains.knowledge.schemas.rag_schema import (
    RAGAnswerResponse,
    RAGQuestionRequest,
)
from src.domains.knowledge.services.rag_service import (
    RAGService,
)


from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from src.core.database.session import (
    get_db,
)
from src.domains.knowledge.schemas.rag_run_schema import (
    RAGRunDetailResponse,
    RAGRunListResponse,
)
from src.domains.knowledge.services.rag_run_query_service import (
    RAGRunQueryService,
)
from src.domains.users.models.user import (
    User,
)
from src.domains.knowledge.schemas.rag_statistics_schema import (
    RAGStatisticsResponse,
)
from src.domains.knowledge.services.rag_statistics_service import (
    RAGStatisticsService,
)
router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge Base"],
)


@router.post(
    "/documents",
    response_model=KnowledgeDocumentResponse,
    status_code=201,
)
def create_knowledge_document(
    request: KnowledgeDocumentCreateRequest,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
):
    service = KnowledgeService(
        db,
    )

    return service.create_and_ingest(
        request,
    )


@router.get(
    "/documents",
    response_model=list[
        KnowledgeDocumentResponse
    ],
)
def list_knowledge_documents(
    category: str | None = None,
    language: str | None = None,
    ingestion_status: str | None = None,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
):
    service = KnowledgeService(
        db,
    )

    return service.list_documents(
        category=category,
        language=language,
        ingestion_status=ingestion_status,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/documents/{document_id}",
    response_model=(
        KnowledgeDocumentDetailResponse
    ),
)
def get_knowledge_document(
    document_id: int,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
):
    service = KnowledgeService(
        db,
    )

    return service.get_document(
        document_id=document_id,
    )


@router.post(
    "/search",
    response_model=KnowledgeSearchResponse,
)
def search_knowledge_base(
    request: KnowledgeSearchRequest,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
):
    retriever = KnowledgeRetriever(
        db,
    )

    return retriever.retrieve(
        request,
    )


@router.post(
    "/ask",
    response_model=RAGAnswerResponse,
)
def ask_knowledge_base(
    request: RAGQuestionRequest,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
):
    service = RAGService(
        db,
    )

    return service.answer(
        request=request,
        user_id=current_user.id,
    )




@router.get(
    "/rag-runs",
    response_model=RAGRunListResponse,
)
def list_rag_runs(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    generation_status: str | None = Query(
        default=None,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(
        get_db,
    ),
) -> RAGRunListResponse:
    service = RAGRunQueryService(
        db,
    )

    return service.list_runs(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        generation_status=(
            generation_status
        ),
    )

@router.get(
    "/rag-runs/statistics",
    response_model=RAGStatisticsResponse,
)
def get_rag_statistics(
    hours: int | None = Query(
        default=None,
        ge=1,
        le=24 * 365,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(
        get_db,
    ),
) -> RAGStatisticsResponse:
    service = RAGStatisticsService(
        db
    )

    return service.get_statistics(
        user_id=current_user.id,
        hours=hours,
    )

@router.get(
    "/rag-runs/{rag_run_id}",
    response_model=RAGRunDetailResponse,
)
def get_rag_run_detail(
    rag_run_id: int,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(
        get_db,
    ),
) -> RAGRunDetailResponse:
    service = RAGRunQueryService(
        db,
    )

    return service.get_run_detail(
        rag_run_id=rag_run_id,
        user_id=current_user.id,
    )

@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_knowledge_document(
    document_id: int,
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(
        get_db,
    ),
) -> Response:
    service = KnowledgeService(
        db=db,
    )

    service.delete_document(
        document_id=document_id,
    )

    return Response(
        status_code=(
            status.HTTP_204_NO_CONTENT
        ),
    )

