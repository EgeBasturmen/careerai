from sqlalchemy.orm import Session

from src.domains.knowledge.retrievers.base import (
    BaseKnowledgeRetriever,
)
from src.domains.knowledge.retrievers.bm25_retriever import (
    BM25KnowledgeRetriever,
)
from src.domains.knowledge.retrievers.hybrid_retriever import (
    HybridKnowledgeRetriever,
)
from src.domains.knowledge.retrievers.semantic_retriever import (
    SemanticKnowledgeRetriever,
)


def get_knowledge_retriever(
    *,
    db: Session,
    retriever_name: str,
    embedding_model_name: str,
) -> BaseKnowledgeRetriever:
    normalized_name = (
        retriever_name
        .strip()
        .lower()
    )

    if normalized_name == "semantic":
        return SemanticKnowledgeRetriever(
            db=db,
            embedding_model_name=(
                embedding_model_name
            ),
        )

    if normalized_name == "bm25":
        return BM25KnowledgeRetriever(
            db=db,
        )

    if normalized_name == "hybrid":
        return HybridKnowledgeRetriever(
            db=db,
            embedding_model_name=(
                embedding_model_name
            ),
        )

    raise ValueError(
        "Unsupported knowledge retriever: "
        f"{retriever_name}"
    )