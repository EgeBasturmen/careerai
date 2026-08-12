"""add source text hash to entity embeddings

Revision ID: 6a0f26eb0cc2
Revises: fd60ed42eadc
Create Date: 2026-07-23 01:15:26.422625

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a0f26eb0cc2'
down_revision: Union[str, Sequence[str], None] = 'fd60ed42eadc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "entity_embeddings",
        sa.Column(
            "source_text_hash",
            sa.String(length=64),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_entity_embeddings_source_text_hash",
        "entity_embeddings",
        ["source_text_hash"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_entity_embeddings_source_text_hash",
        table_name="entity_embeddings",
    )

    op.drop_column(
        "entity_embeddings",
        "source_text_hash",
    )
