"""paper text highlights

Revision ID: b2c9a7f41d3e
Revises: ee1d6aa1589a
Create Date: 2026-09-19 15:20:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2c9a7f41d3e"
down_revision: Union[str, Sequence[str], None] = "ee1d6aa1589a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the highlights column. Nullable, so existing papers need no backfill
    -- absent and empty both mean "nothing highlighted"."""
    with op.batch_alter_table("paper") as batch_op:
        batch_op.add_column(sa.Column("highlights", sa.JSON(), nullable=True))


def downgrade() -> None:
    """Drop it. This discards any highlights, which exist nowhere else."""
    with op.batch_alter_table("paper") as batch_op:
        batch_op.drop_column("highlights")
