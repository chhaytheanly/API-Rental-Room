"""create users table

Revision ID: c9eccbbd166f
Revises: 40d920b1319c
Create Date: 2026-02-26 16:20:15.944737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9eccbbd166f'
down_revision: Union[str, Sequence[str], None] = '40d920b1319c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
