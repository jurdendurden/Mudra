"""expand item system with socketing and enchanting

Revision ID: f1g2h3i4j5k6
Revises: fdbeff902f39
Create Date: 2025-10-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'f1g2h3i4j5k6'
down_revision = 'fdbeff902f39'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to item_templates table
    with op.batch_alter_table('item_templates', schema=None) as batch_op:
        # Item type classification
        batch_op.add_column(sa.Column('item_type', sa.Integer(), nullable=True, server_default='13'))
        batch_op.add_column(sa.Column('material', sa.String(length=50), nullable=True))
        
        # Item flags
        batch_op.add_column(sa.Column('item_flags', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('item_flags_2', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('wear_flags', sa.JSON(), nullable=True))
        
        # Socket system
        batch_op.add_column(sa.Column('socket_count', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('socket_types', sa.JSON(), nullable=True))
        
        # Weapon-specific properties
        batch_op.add_column(sa.Column('weapon_type', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('weapon_flags', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('base_damage_min', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('base_damage_max', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('attack_speed', sa.Float(), nullable=True, server_default='1.0'))
        batch_op.add_column(sa.Column('damage_types', sa.JSON(), nullable=True))
        
        # Armor-specific properties
        batch_op.add_column(sa.Column('armor_class', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('armor_slot', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('damage_reduction', sa.JSON(), nullable=True))
        
        # Container properties
        batch_op.add_column(sa.Column('container_capacity', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('container_weight_capacity', sa.Float(), nullable=True, server_default='0.0'))
        
        # Consumable properties
        batch_op.add_column(sa.Column('consumable_charges', sa.Integer(), nullable=True, server_default='1'))
        batch_op.add_column(sa.Column('consumable_effects', sa.JSON(), nullable=True))
        
        # Crafting properties
        batch_op.add_column(sa.Column('crafting_skill', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('crafting_difficulty', sa.Integer(), nullable=True, server_default='1'))
        
        # Durability
        batch_op.add_column(sa.Column('max_durability', sa.Integer(), nullable=True, server_default='100'))
        
        # Enchantability
        batch_op.add_column(sa.Column('max_enchantments', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('enchantable', sa.Boolean(), nullable=True, server_default='1'))

    # Add new columns to items table
    with op.batch_alter_table('items', schema=None) as batch_op:
        # Durability
        batch_op.add_column(sa.Column('current_durability', sa.Integer(), nullable=True))
        
        # Socket system
        batch_op.add_column(sa.Column('sockets', sa.JSON(), nullable=True))
        
        # Weapon modifications
        batch_op.add_column(sa.Column('sharpness', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('balance', sa.Integer(), nullable=True, server_default='0'))
        
        # Custom modifications
        batch_op.add_column(sa.Column('custom_name', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('custom_flags', sa.JSON(), nullable=True))
        
        # Crafting info
        batch_op.add_column(sa.Column('crafted_by_name', sa.String(length=100), nullable=True))
        
        # Equipment tracking
        batch_op.add_column(sa.Column('equipped_slot', sa.String(length=50), nullable=True))
        
        # Metadata
        batch_op.add_column(sa.Column('last_repaired_at', sa.DateTime(), nullable=True))


def downgrade():
    # Remove columns from items table
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.drop_column('last_repaired_at')
        batch_op.drop_column('equipped_slot')
        batch_op.drop_column('crafted_by_name')
        batch_op.drop_column('custom_flags')
        batch_op.drop_column('custom_name')
        batch_op.drop_column('balance')
        batch_op.drop_column('sharpness')
        batch_op.drop_column('sockets')
        batch_op.drop_column('current_durability')

    # Remove columns from item_templates table
    with op.batch_alter_table('item_templates', schema=None) as batch_op:
        batch_op.drop_column('enchantable')
        batch_op.drop_column('max_enchantments')
        batch_op.drop_column('max_durability')
        batch_op.drop_column('crafting_difficulty')
        batch_op.drop_column('crafting_skill')
        batch_op.drop_column('consumable_effects')
        batch_op.drop_column('consumable_charges')
        batch_op.drop_column('container_weight_capacity')
        batch_op.drop_column('container_capacity')
        batch_op.drop_column('damage_reduction')
        batch_op.drop_column('armor_slot')
        batch_op.drop_column('armor_class')
        batch_op.drop_column('damage_types')
        batch_op.drop_column('attack_speed')
        batch_op.drop_column('base_damage_max')
        batch_op.drop_column('base_damage_min')
        batch_op.drop_column('weapon_flags')
        batch_op.drop_column('weapon_type')
        batch_op.drop_column('socket_types')
        batch_op.drop_column('socket_count')
        batch_op.drop_column('wear_flags')
        batch_op.drop_column('item_flags_2')
        batch_op.drop_column('item_flags')
        batch_op.drop_column('material')
        batch_op.drop_column('item_type')

