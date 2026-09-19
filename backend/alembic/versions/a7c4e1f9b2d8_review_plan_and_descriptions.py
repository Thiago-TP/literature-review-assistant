"""review plan and field/tag descriptions

Revision ID: a7c4e1f9b2d8
Revises: b2c9a7f41d3e
Create Date: 2026-09-19 18:05:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a7c4e1f9b2d8"
down_revision: Union[str, Sequence[str], None] = "b2c9a7f41d3e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the review plan's five prose sections to `project`, and a
    description to every field and tag. All nullable, so existing reviews need
    no backfill -- null and empty both mean "not written yet", which is the
    state every review starts in anyway."""
    with op.batch_alter_table("project") as batch_op:
        batch_op.add_column(sa.Column("plan_purpose", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("plan_scope", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("plan_search", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("plan_weights", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("plan_other", sa.Text(), nullable=True))

    with op.batch_alter_table("tagfield") as batch_op:
        batch_op.add_column(sa.Column("description", sa.Text(), nullable=True))

    with op.batch_alter_table("tagoption") as batch_op:
        batch_op.add_column(sa.Column("description", sa.Text(), nullable=True))


def downgrade() -> None:
    """Drop all seven columns. This discards the whole review plan, which is
    written by hand and exists nowhere else -- there is no export carrying it
    and no way to recover it."""
    with op.batch_alter_table("tagoption") as batch_op:
        batch_op.drop_column("description")

    with op.batch_alter_table("tagfield") as batch_op:
        batch_op.drop_column("description")

    with op.batch_alter_table("project") as batch_op:
        batch_op.drop_column("plan_other")
        batch_op.drop_column("plan_weights")
        batch_op.drop_column("plan_search")
        batch_op.drop_column("plan_scope")
        batch_op.drop_column("plan_purpose")
