"""initial schema

Revision ID: 89e168e3f7aa
Revises:
Create Date: 2026-08-07 15:24:11.347359

"""
from typing import Sequence, Union

import sqlmodel
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89e168e3f7aa'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    `project` and `paper` reference each other (paper.project_id -> project.id,
    project.last_viewed_paper_id -> paper.id), so the FK from project to paper
    is added in a separate step after both tables exist, avoiding a
    create-order deadlock.
    """
    op.create_table(
        'project',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_viewed_paper_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_project_name'), 'project', ['name'], unique=True)

    op.create_table(
        'paper',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('abstract', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('doi', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('doi_normalized', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('title_normalized', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('authors', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('source_title', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('notes', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('source', sa.Enum('XLSX_IMPORT', 'CROSSREF_DOI', 'CROSSREF_TITLE', 'MANUAL', name='papersource'), nullable=False),
        sa.Column('raw_metadata', sa.JSON(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_paper_doi_normalized'), 'paper', ['doi_normalized'], unique=False)
    op.create_index('ix_paper_project_doi_normalized_unique', 'paper', ['project_id', 'doi_normalized'], unique=True, sqlite_where=sa.text('doi_normalized IS NOT NULL'))
    op.create_index(op.f('ix_paper_project_id'), 'paper', ['project_id'], unique=False)
    op.create_index(op.f('ix_paper_title_normalized'), 'paper', ['title_normalized'], unique=False)

    with op.batch_alter_table('project') as batch_op:
        batch_op.create_foreign_key(
            'fk_project_last_viewed_paper_id_paper', 'paper', ['last_viewed_paper_id'], ['id'], ondelete='SET NULL'
        )

    op.create_table(
        'tagfield',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('is_protected', sa.Boolean(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_tagfield_project_id'), 'tagfield', ['project_id'], unique=False)
    op.create_index('ix_tagfield_project_name_unique', 'tagfield', ['project_id', 'name'], unique=True)

    op.create_table(
        'tagoption',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('field_id', sa.Integer(), nullable=False),
        sa.Column('value', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['field_id'], ['tagfield.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_tagoption_field_id'), 'tagoption', ['field_id'], unique=False)
    op.create_index('ix_tagoption_field_value_unique', 'tagoption', ['field_id', 'value'], unique=True)

    op.create_table(
        'tagassignment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('paper_id', sa.Integer(), nullable=False),
        sa.Column('tag_option_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['paper_id'], ['paper.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_option_id'], ['tagoption.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_tagassignment_paper_id'), 'tagassignment', ['paper_id'], unique=False)
    op.create_index('ix_tagassignment_paper_option_unique', 'tagassignment', ['paper_id', 'tag_option_id'], unique=True)
    op.create_index(op.f('ix_tagassignment_tag_option_id'), 'tagassignment', ['tag_option_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_tagassignment_tag_option_id'), table_name='tagassignment')
    op.drop_index('ix_tagassignment_paper_option_unique', table_name='tagassignment')
    op.drop_index(op.f('ix_tagassignment_paper_id'), table_name='tagassignment')
    op.drop_table('tagassignment')
    op.drop_index('ix_tagoption_field_value_unique', table_name='tagoption')
    op.drop_index(op.f('ix_tagoption_field_id'), table_name='tagoption')
    op.drop_table('tagoption')
    op.drop_index('ix_tagfield_project_name_unique', table_name='tagfield')
    op.drop_index(op.f('ix_tagfield_project_id'), table_name='tagfield')
    op.drop_table('tagfield')
    op.drop_index(op.f('ix_paper_title_normalized'), table_name='paper')
    op.drop_index(op.f('ix_paper_project_id'), table_name='paper')
    op.drop_index('ix_paper_project_doi_normalized_unique', table_name='paper', sqlite_where=sa.text('doi_normalized IS NOT NULL'))
    op.drop_index(op.f('ix_paper_doi_normalized'), table_name='paper')
    op.drop_table('paper')
    op.drop_index(op.f('ix_project_name'), table_name='project')
    op.drop_table('project')
