"""add embedding counters to job ingestion runs

Revision ID: 9d117b156958
Revises: 6a0f26eb0cc2
Create Date: 2026-07-23 01:51:10.014018

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d117b156958'
down_revision: Union[str, Sequence[str], None] = '6a0f26eb0cc2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "job_ingestion_runs",
        sa.Column(
            "embedding_created_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )

    op.add_column(
        "job_ingestion_runs",
        sa.Column(
            "embedding_updated_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )

    op.add_column(
        "job_ingestion_runs",
        sa.Column(
            "embedding_skipped_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "job_ingestion_runs",
        "embedding_skipped_count",
    )

    op.drop_column(
        "job_ingestion_runs",
        "embedding_updated_count",
    )

    op.drop_column(
        "job_ingestion_runs",
        "embedding_created_count",
    )