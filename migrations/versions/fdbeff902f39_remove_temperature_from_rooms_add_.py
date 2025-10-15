"""remove_temperature_from_rooms_add_climate_to_areas

Revision ID: fdbeff902f39
Revises: a7308962ab04
Create Date: 2025-10-14 16:22:14.955836

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fdbeff902f39'
down_revision = 'a7308962ab04'
branch_labels = None
depends_on = None


def upgrade():
    # Remove temperature column from rooms table
    with op.batch_alter_table('rooms', schema=None) as batch_op:
        batch_op.drop_column('temperature')
    
    # Add climate column to areas table
    with op.batch_alter_table('areas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('climate', sa.String(length=20), nullable=True, server_default='temperate'))


def downgrade():
    # Remove climate column from areas table
    with op.batch_alter_table('areas', schema=None) as batch_op:
        batch_op.drop_column('climate')
    
    # Add back temperature column to rooms table
    with op.batch_alter_table('rooms', schema=None) as batch_op:
        batch_op.add_column(sa.Column('temperature', sa.String(length=20), nullable=True, server_default='normal'))
