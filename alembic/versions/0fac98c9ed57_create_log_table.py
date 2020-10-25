"""create log table

Revision ID: 0fac98c9ed57
Revises: 
Create Date: 2020-10-17 19:26:06.288130

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0fac98c9ed57'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'log',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('uuid', sa.String(50), nullable=False),
        sa.Column('ip', sa.String(50), nullable=False),
        sa.Column('timestamp', sa.String(50), nullable=False),
    )


def downgrade():
    op.drop_table('log')
