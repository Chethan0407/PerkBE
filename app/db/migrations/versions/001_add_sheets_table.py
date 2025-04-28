"""add sheets table

Revision ID: 001
Revises: 
Create Date: 2024-04-27 08:48:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'sheets',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('data', postgresql.JSONB(), server_default='[]'),
        sa.Column('sheets', postgresql.JSONB(), server_default='[]')
    )

def downgrade():
    op.drop_table('sheets') 