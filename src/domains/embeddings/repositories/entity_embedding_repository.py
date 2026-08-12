from sqlalchemy.orm import Session

from src.domains.embeddings.models.entity_embedding import (
    EntityEmbedding,
)


class EntityEmbeddingRepository:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def get_by_entity_and_model(
        self,
        entity_type: str,
        entity_id: int,
        model_name: str,
    ) -> EntityEmbedding | None:
        return (
            self.db.query(EntityEmbedding)
            .filter(
                EntityEmbedding.entity_type
                == entity_type,
                EntityEmbedding.entity_id
                == entity_id,
                EntityEmbedding.model_name
                == model_name,
            )
            .first()
        )

    def update_source_text_hash(
        self,
        *,
        entity_embedding: EntityEmbedding,
        source_text_hash: str,
    ) -> EntityEmbedding:
        entity_embedding.source_text_hash = (
            source_text_hash
        )

        self.db.flush()

        return entity_embedding

    def upsert(
        self,
        *,
        entity_type: str,
        entity_id: int,
        provider: str,
        model_name: str,
        dimension: int,
        source_text: str,
        source_text_hash: str,
        embedding: list[float],
    ) -> EntityEmbedding:
        existing = self.get_by_entity_and_model(
            entity_type=entity_type,
            entity_id=entity_id,
            model_name=model_name,
        )

        if existing is not None:
            existing.provider = provider
            existing.dimension = dimension
            existing.source_text = source_text
            existing.source_text_hash = (
                source_text_hash
            )
            existing.embedding = embedding

            self.db.flush()

            return existing

        entity_embedding = EntityEmbedding(
            entity_type=entity_type,
            entity_id=entity_id,
            provider=provider,
            model_name=model_name,
            dimension=dimension,
            source_text=source_text,
            source_text_hash=source_text_hash,
            embedding=embedding,
        )

        self.db.add(entity_embedding)
        self.db.flush()

        return entity_embedding