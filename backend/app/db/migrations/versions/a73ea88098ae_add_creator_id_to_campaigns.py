"""add_creator_id_to_campaigns

Revision ID: a73ea88098ae
Revises: ca6c8ca4ae1a
Create Date: 2026-09-10 22:19:07.992487
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a73ea88098ae'
down_revision: Union[str, None] = 'ca6c8ca4ae1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('campaigns', sa.Column('creator_id', sa.Uuid(), nullable=True))
    op.create_foreign_key('fk_campaigns_creator_id_users', 'campaigns', 'users', ['creator_id'], ['id'], ondelete='SET NULL')
    op.create_index(op.f('ix_campaigns_creator_id'), 'campaigns', ['creator_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_campaigns_creator_id'), table_name='campaigns')
    op.drop_constraint('fk_campaigns_creator_id_users', 'campaigns', type_='foreignkey')
    op.drop_column('campaigns', 'creator_id')
