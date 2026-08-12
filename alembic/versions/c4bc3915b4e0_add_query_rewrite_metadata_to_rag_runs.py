"""add query rewrite metadata to rag runs

Revision ID: c4bc3915b4e0
Revises: 9a0f3ff3df19
Create Date: 2026-07-20 12:54:01.249779

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4bc3915b4e0'
down_revision: Union[str, Sequence[str], None] = '9a0f3ff3df19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "rag_runs",
        sa.Column(
            "rewrite_provider",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "rag_runs",
        sa.Column(
            "rewrite_model_name",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "rag_runs",
        sa.Column(
            "original_query",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "rag_runs",
        sa.Column(
            "rewritten_query",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "rag_runs",
        sa.Column(
            "was_rewritten",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "rag_runs",
        sa.Column(
            "rewrite_latency_ms",
            sa.Float(),
            nullable=True,
        ),
    )

    op.add_column(
        "rag_runs",
        sa.Column(
            "rewrite_fallback_used",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "rag_runs",
        sa.Column(
            "rewrite_fallback_reason",
            sa.Text(),
            nullable=True,
        ),
    )

    op.create_index(
        op.f(
            "ix_rag_runs_rewrite_model_name"
        ),
        "rag_runs",
        ["rewrite_model_name"],
        unique=False,
    )

    op.alter_column(
        "rag_runs",
        "was_rewritten",
        server_default=None,
    )

    op.alter_column(
        "rag_runs",
        "rewrite_fallback_used",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_index(
        op.f(
            "ix_rag_runs_rewrite_model_name"
        ),
        table_name="rag_runs",
    )

    op.drop_column(
        "rag_runs",
        "rewrite_fallback_reason",
    )

    op.drop_column(
        "rag_runs",
        "rewrite_fallback_used",
    )

    op.drop_column(
        "rag_runs",
        "rewrite_latency_ms",
    )

    op.drop_column(
        "rag_runs",
        "was_rewritten",
    )

    op.drop_column(
        "rag_runs",
        "rewritten_query",
    )

    op.drop_column(
        "rag_runs",
        "original_query",
    )

    op.drop_column(
        "rag_runs",
        "rewrite_model_name",
    )

    op.drop_column(
        "rag_runs",
        "rewrite_provider",
    )
