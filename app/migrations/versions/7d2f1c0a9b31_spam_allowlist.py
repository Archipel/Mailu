"""per-user spam allowlist

Revision ID: 7d2f1c0a9b31
Revises: 3b7eee912b41
Create Date: 2026-11-13 20:00:00

"""

# revision identifiers, used by Alembic.
revision = '7d2f1c0a9b31'
down_revision = '3b7eee912b41'

from alembic import op
import sqlalchemy as sa


def upgrade():
    with op.batch_alter_table('user') as batch:
        batch.add_column(sa.Column('spam_allowlist', sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table('user') as batch:
        batch.drop_column('spam_allowlist')
