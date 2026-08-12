"""enable pgvector extension

Revision ID: 515dff0a3a2c
Revises: 5f2e1a76484d
Create Date: 2026-07-14 12:25:19.357386

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '515dff0a3a2c'
down_revision: Union[str, Sequence[str], None] = '5f2e1a76484d'
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE EXTENSION IF NOT EXISTS vector"
    )


def downgrade() -> None:
    op.execute(
        "DROP EXTENSION IF EXISTS vector"
    )
