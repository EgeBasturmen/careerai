from src.core.config.settings import settings
from src.domains.embeddings.clients.base import (
    EmbeddingClient,
)
from src.domains.embeddings.clients.fake_embedding_client import (
    FakeEmbeddingClient,
)
from src.domains.embeddings.clients.sentence_transformer_embedding_client import (
    SentenceTransformerEmbeddingClient,
)


def get_embedding_client() -> EmbeddingClient:
    if settings.embedding_provider == "fake":
        return FakeEmbeddingClient()

    if (
        settings.embedding_provider
        == "sentence_transformer"
    ):
        return SentenceTransformerEmbeddingClient()

    raise ValueError(
        "Unsupported embedding provider: "
        f"{settings.embedding_provider}"
    )