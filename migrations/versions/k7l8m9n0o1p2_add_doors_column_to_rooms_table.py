"""add doors column to rooms table

Revision ID: k7l8m9n0o1p2
Revises: f1g2h3i4j5k6
Create Date: 2025-10-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'k7l8m9n0o1p2'
down_revision = '18052f65c6d7'
branch_labels = None
depends_on = None


def upgrade():
    # Add doors column to rooms table
    op.add_column('rooms', sa.Column('doors', sa.JSON(), nullable=True))
    
    # Set default value for existing rows
    op.execute("UPDATE rooms SET doors = '{}' WHERE doors IS NULL")


def downgrade():
    # Remove doors column
    op.drop_column('rooms', 'doors')

