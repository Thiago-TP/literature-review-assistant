"""paper rating as float for half-star ratings

Revision ID: ee1d6aa1589a
Revises: c379c1f66660
Create Date: 2026-08-12 08:33:30.716979

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee1d6aa1589a'
down_revision: Union[str, Sequence[str], None] = 'c379c1f66660'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('paper') as batch_op:
        batch_op.alter_column('rating',
                   existing_type=sa.INTEGER(),
                   type_=sa.Float(),
                   existing_nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('paper') as batch_op:
        batch_op.alter_column('rating',
                   existing_type=sa.Float(),
                   type_=sa.INTEGER(),
                   existing_nullable=True)
