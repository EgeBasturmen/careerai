from src.core.config.settings import settings
from src.domains.knowledge.rerankers.base import (
    BaseKnowledgeReranker,
)
from src.domains.knowledge.rerankers.cross_encoder_reranker import (
    CrossEncoderKnowledgeReranker,
)


def get_knowledge_reranker(
) -> BaseKnowledgeReranker | None:
    if not settings.knowledge_reranker_enabled:
        return None

    return CrossEncoderKnowledgeReranker(
        model_name=(
            settings.knowledge_reranker_model_name
        ),
        batch_size=(
            settings.knowledge_reranker_batch_size
        ),
    )