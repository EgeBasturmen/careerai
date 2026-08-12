from collections.abc import Sequence

from sentence_transformers import SentenceTransformer

from src.core.config.settings import settings
from src.domains.embeddings.clients.base import (
    EmbeddingClient,
)


class SentenceTransformerEmbeddingClient(
    EmbeddingClient
):
    def __init__(
        self,
        model_name: str | None = None,
        device: str | None = None,
        batch_size: int | None = None,
        normalize_embeddings: bool | None = None,
    ):
        self._model_name = (
            model_name
            or settings.embedding_model_name
        )

        self.device = (
            device
            or settings.embedding_device
        )

        self.batch_size = (
            batch_size
            or settings.embedding_batch_size
        )

        self.normalize_embeddings = (
            settings.embedding_normalize
            if normalize_embeddings is None
            else normalize_embeddings
        )

        self.model = SentenceTransformer(
            self._model_name,
            device=self.device,
        )

        self._embedding_dimension = (
            self.model.get_sentence_embedding_dimension()
        )

        if self._embedding_dimension is None:
            raise ValueError(
                "Embedding model did not report "
                "an embedding dimension"
            )

    @property
    def provider_name(
        self,
    ) -> str:
        return "sentence_transformer"

    @property
    def model_name(
        self,
    ) -> str:
        return self._model_name

    @property
    def embedding_dimension(
        self,
    ) -> int:
        return self._embedding_dimension

    def embed_text(
        self,
        text: str,
    ) -> list[float]:
        normalized_text = self._validate_text(
            text
        )

        embedding = self.model.encode(
            normalized_text,
            convert_to_numpy=True,
            normalize_embeddings=(
                self.normalize_embeddings
            ),
            show_progress_bar=False,
        )

        return embedding.astype(
            float
        ).tolist()

    def embed_texts(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        normalized_texts = [
            self._validate_text(text)
            for text in texts
        ]

        if not normalized_texts:
            return []

        embeddings = self.model.encode(
            normalized_texts,
            batch_size=self.batch_size,
            convert_to_numpy=True,
            normalize_embeddings=(
                self.normalize_embeddings
            ),
            show_progress_bar=False,
        )

        return [
            embedding.astype(float).tolist()
            for embedding in embeddings
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