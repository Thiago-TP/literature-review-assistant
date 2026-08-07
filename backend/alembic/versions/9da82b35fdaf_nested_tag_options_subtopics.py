"""nested tag options (subtopics)

Revision ID: 9da82b35fdaf
Revises: 89e168e3f7aa
Create Date: 2026-08-07 16:17:17.207972

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9da82b35fdaf'
down_revision: Union[str, Sequence[str], None] = '89e168e3f7aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(op.f('ix_tagoption_field_value_unique'), table_name='tagoption')

    with op.batch_alter_table('tagoption') as batch_op:
        batch_op.add_column(sa.Column('parent_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_tagoption_parent_id_tagoption', 'tagoption', ['parent_id'], ['id'], ondelete='CASCADE'
        )

    op.create_index(op.f('ix_tagoption_parent_id'), 'tagoption', ['parent_id'], unique=False)
    op.create_index('ix_tagoption_parent_value_unique', 'tagoption', ['parent_id', 'value'], unique=True, sqlite_where=sa.text('parent_id IS NOT NULL'))
    op.create_index('ix_tagoption_root_value_unique', 'tagoption', ['field_id', 'value'], unique=True, sqlite_where=sa.text('parent_id IS NULL'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_tagoption_root_value_unique', table_name='tagoption', sqlite_where=sa.text('parent_id IS NULL'))
    op.drop_index('ix_tagoption_parent_value_unique', table_name='tagoption', sqlite_where=sa.text('parent_id IS NOT NULL'))
    op.drop_index(op.f('ix_tagoption_parent_id'), table_name='tagoption')

    with op.batch_alter_table('tagoption') as batch_op:
        batch_op.drop_constraint('fk_tagoption_parent_id_tagoption', type_='foreignkey')
        batch_op.drop_column('parent_id')

    op.create_index(op.f('ix_tagoption_field_value_unique'), 'tagoption', ['field_id', 'value'], unique=True)
