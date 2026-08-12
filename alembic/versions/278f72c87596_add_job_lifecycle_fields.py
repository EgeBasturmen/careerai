"""add job lifecycle fields

Revision ID: 278f72c87596
Revises: 9d117b156958
Create Date: 2026-07-23 02:02:09.943667

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '278f72c87596'
down_revision: Union[str, Sequence[str], None] = '9d117b156958'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    op.add_column(
        "jobs",
        sa.Column(
            "first_seen_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.add_column(
        "jobs",
        sa.Column(
            "last_seen_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.add_column(
        "jobs",
        sa.Column(
            "deactivated_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_jobs_is_active",
        "jobs",
        ["is_active"],
    )

    op.create_index(
        "ix_jobs_last_seen_at",
        "jobs",
        ["last_seen_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_jobs_last_seen_at",
        table_name="jobs",
    )

    op.drop_index(
        "ix_jobs_is_active",
        table_name="jobs",
    )

    op.drop_column(
        "jobs",
        "deactivated_at",
    )

    op.drop_column(
        "jobs",
        "last_seen_at",
    )

    op.drop_column(
        "jobs",
        "first_seen_at",
    )

    op.drop_column(
        "jobs",
        "is_active",
    )
