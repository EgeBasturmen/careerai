from abc import ABC, abstractmethod
from collections.abc import Sequence


class EmbeddingClient(ABC):
    @property
    @abstractmethod
    def provider_name(
        self,
    ) -> str:
        """Embedding sağlayıcısının kısa adı."""
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(
        self,
    ) -> str:
        """Kullanılan embedding modelinin adı."""
        raise NotImplementedError

    @property
    @abstractmethod
    def embedding_dimension(
        self,
    ) -> int:
        """Modelin ürettiği vektör boyutu."""
        raise NotImplementedError

    @abstractmethod
    def embed_text(
        self,
        text: str,
    ) -> list[float]:
        """Tek bir metni vektöre dönüştürür."""
        raise NotImplementedError

    @abstractmethod
    def embed_texts(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        """Birden fazla metni batch olarak vektöre dönüştürür."""
        raise NotImplementedError