"""add rag retrieval observability fields

Revision ID: 9a0f3ff3df19
Revises: eb4cf8841cd9
Create Date: 2026-07-20 01:20:00.465828

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "9a0f3ff3df19"
down_revision: Union[
    str,
    Sequence[str],
    None,
] = "eb4cf8841cd9"

branch_labels: Union[
    str,
    Sequence[str],
    None,
] = None

depends_on: Union[
    str,
    Sequence[str],
    None,
] = None


def upgrade() -> None:
    op.add_column(
        "rag_runs",
        sa.Column(
            "candidate_result_count",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )

    op.add_column(
        "rag_runs",
        sa.Column(
            "retriever_name",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "rag_runs",
        sa.Column(
            "reranker_name",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "rag_runs",
        sa.Column(
            "reranker_model_name",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.alter_column(
        "rag_runs",
        "candidate_result_count",
        server_default=None,
    )

    op.create_index(
        op.f(
            "ix_rag_runs_retriever_name"
        ),
        "rag_runs",
        ["retriever_name"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_rag_runs_reranker_name"
        ),
        "rag_runs",
        ["reranker_name"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_rag_runs_reranker_model_name"
        ),
        "rag_runs",
        ["reranker_model_name"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f(
            "ix_rag_runs_reranker_model_name"
        ),
        table_name="rag_runs",
    )

    op.drop_index(
        op.f(
            "ix_rag_runs_reranker_name"
        ),
        table_name="rag_runs",
    )

    op.drop_index(
        op.f(
            "ix_rag_runs_retriever_name"
        ),
        table_name="rag_runs",
    )

    op.drop_column(
        "rag_runs",
        "reranker_model_name",
    )

    op.drop_column(
        "rag_runs",
        "reranker_name",
    )

    op.drop_column(
        "rag_runs",
        "retriever_name",
    )

    op.drop_column(
        "rag_runs",
        "candidate_result_count",
    )