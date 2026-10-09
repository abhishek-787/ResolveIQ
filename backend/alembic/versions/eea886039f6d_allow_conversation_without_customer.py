"""allow conversation without customer

Revision ID: eea886039f6d
Revises: 5057209d5150
Create Date: 2026-10-06 13:20:13.240229

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eea886039f6d'
down_revision: Union[str, Sequence[str], None] = '5057209d5150'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.alter_column(
        "conversations",
        "customer_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    """Upgrade schema."""
    pass


def downgrade() -> None:

    op.alter_column(
        "conversations",
        "customer_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    """Downgrade schema."""
    pass
