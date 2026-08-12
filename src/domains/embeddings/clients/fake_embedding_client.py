import hashlib
from collections.abc import Sequence

from src.domains.embeddings.clients.base import (
    EmbeddingClient,
)


class FakeEmbeddingClient(EmbeddingClient):
    DIMENSION = 8

    @property
    def provider_name(
        self,
    ) -> str:
        return "fake"

    @property
    def model_name(
        self,
    ) -> str:
        return "fake-deterministic-v1"

    @property
    def embedding_dimension(
        self,
    ) -> int:
        return self.DIMENSION

    def embed_text(
        self,
        text: str,
    ) -> list[float]:
        normalized_text = self._validate_text(
            text,
        )

        digest = hashlib.sha256(
            normalized_text.encode("utf-8")
        ).digest()

        vector = [
            self._byte_to_float(value)
            for value in digest[: self.DIMENSION]
        ]

        return vector

    def embed_texts(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        if not texts:
            return []

        return [
            self.embed_text(text)
            for text in texts
        ]

    def _validate_text(
        self,
        text: str,
    ) -> str:
        normalized_text = text.strip()

        if not normalized_text:
            raise ValueError(
                "Text cannot be empty"
            )

        return normalized_text

    def _byte_to_float(
        self,
        value: int,
    ) -> float:
        return (
            value / 127.5
        ) - 1.0