"""add chunked document status

Revision ID: d40bd488a71c
Revises: ed84162aecd5
Create Date: 2026-10-02 11:34:06.591552
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "d40bd488a71c"
down_revision: Union[str, Sequence[str], None] = "ed84162aecd5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add CHUNKED to PostgreSQL document_status enum."""

    op.execute(
        "ALTER TYPE document_status "
        "ADD VALUE IF NOT EXISTS 'CHUNKED'"
    )


def downgrade() -> None:
    """PostgreSQL enum values are not removed automatically."""
    pass