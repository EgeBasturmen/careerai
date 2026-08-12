from collections.abc import Sequence

from src.domains.embeddings.clients.base import (
    EmbeddingClient,
)
from src.domains.embeddings.schemas.embedding_schema import (
    BatchEmbeddingResult,
    EmbeddingResult,
)


class EmbeddingService:
    def __init__(
        self,
        client: EmbeddingClient,
    ):
        self.client = client

    def embed_text(
        self,
        text: str,
    ) -> EmbeddingResult:
        vector = self.client.embed_text(
            text,
        )

        self._validate_vector(
            vector,
        )

        return EmbeddingResult(
            provider=self.client.provider_name,
            model=self.client.model_name,
            dimension=self.client.embedding_dimension,
            vector=vector,
        )

    def embed_texts(
        self,
        texts: Sequence[str],
    ) -> BatchEmbeddingResult:
        vectors = self.client.embed_texts(
            texts,
        )

        for vector in vectors:
            self._validate_vector(
                vector,
            )

        if len(vectors) != len(texts):
            raise ValueError(
                "Embedding client returned an unexpected "
                "number of vectors"
            )

        return BatchEmbeddingResult(
            provider=self.client.provider_name,
            model=self.client.model_name,
            dimension=self.client.embedding_dimension,
            vectors=vectors,
        )

    def _validate_vector(
        self,
        vector: list[float],
    ) -> None:
        expected_dimension = (
            self.client.embedding_dimension
        )

        if len(vector) != expected_dimension:
            raise ValueError(
                "Invalid embedding dimension. "
                f"Expected {expected_dimension}, "
                f"received {len(vector)}"
            )

        if not all(
            isinstance(value, float)
            for value in vector
        ):
            raise TypeError(
                "Embedding vector must contain only floats"
            )