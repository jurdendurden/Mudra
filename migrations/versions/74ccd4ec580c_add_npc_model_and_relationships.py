"""add_npc_model_and_relationships

Revision ID: 74ccd4ec580c
Revises: k7l8m9n0o1p2
Create Date: 2025-10-20 12:50:03.149706

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74ccd4ec580c'
down_revision = 'k7l8m9n0o1p2'
branch_labels = None
depends_on = None


def upgrade():
    # Create NPCs table
    op.create_table('npcs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('npc_id', sa.String(length=80), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('race', sa.String(length=50), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('current_room_id', sa.Integer(), nullable=True),
    sa.Column('x_coord', sa.Integer(), nullable=True),
    sa.Column('y_coord', sa.Integer(), nullable=True),
    sa.Column('z_coord', sa.Integer(), nullable=True),
    sa.Column('attributes', sa.JSON(), nullable=True),
    sa.Column('max_hp', sa.Integer(), nullable=True),
    sa.Column('current_hp', sa.Integer(), nullable=True),
    sa.Column('max_mana', sa.Integer(), nullable=True),
    sa.Column('current_mana', sa.Integer(), nullable=True),
    sa.Column('max_movement', sa.Integer(), nullable=True),
    sa.Column('current_movement', sa.Integer(), nullable=True),
    sa.Column('trial_points', sa.Integer(), nullable=True),
    sa.Column('progress_points', sa.Integer(), nullable=True),
    sa.Column('gold', sa.Integer(), nullable=True),
    sa.Column('silver', sa.Integer(), nullable=True),
    sa.Column('copper', sa.Integer(), nullable=True),
    sa.Column('avatar', sa.String(length=50), nullable=True),
    sa.Column('skills', sa.JSON(), nullable=True),
    sa.Column('spells', sa.JSON(), nullable=True),
    sa.Column('ai_behavior', sa.String(length=50), nullable=True),
    sa.Column('is_hostile', sa.Boolean(), nullable=True),
    sa.Column('respawn_time', sa.Integer(), nullable=True),
    sa.Column('loot_table', sa.JSON(), nullable=True),
    sa.Column('dialogue', sa.JSON(), nullable=True),
    sa.Column('faction', sa.String(length=50), nullable=True),
    sa.Column('reputation_required', sa.Integer(), nullable=True),
    sa.Column('is_unique', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['current_room_id'], ['rooms.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_npcs_name'), 'npcs', ['name'], unique=True)
    op.create_index(op.f('ix_npcs_npc_id'), 'npcs', ['npc_id'], unique=True)
    
    # Add NPC ownership columns to items table
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('owner_npc_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('equipped_npc_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_items_owner_npc_id', 'npcs', ['owner_npc_id'], ['id'])
        batch_op.create_foreign_key('fk_items_equipped_npc_id', 'npcs', ['equipped_npc_id'], ['id'])


def downgrade():
    # Remove NPC ownership columns from items table
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.drop_constraint('fk_items_equipped_npc_id', type_='foreignkey')
        batch_op.drop_constraint('fk_items_owner_npc_id', type_='foreignkey')
        batch_op.drop_column('equipped_npc_id')
        batch_op.drop_column('owner_npc_id')
    
    # Drop NPCs table
    op.drop_index(op.f('ix_npcs_npc_id'), table_name='npcs')
    op.drop_index(op.f('ix_npcs_name'), table_name='npcs')
    op.drop_table('npcs')
