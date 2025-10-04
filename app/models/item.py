from app import db
from datetime import datetime
import json

class ItemTemplate(db.Model):
    """Template for items - defines base properties"""
    __tablename__ = 'item_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    base_type = db.Column(db.String(100), nullable=False)  # e.g., 'weapon.blade.sword'
    subtype = db.Column(db.String(100))
    
    # Base properties
    weight = db.Column(db.Float, default=0.0)
    value = db.Column(db.Integer, default=0)
    quality_tier = db.Column(db.String(20), default='common')  # poor, common, good, rare, epic, legendary
    
    # Component requirements for crafting
    components_required = db.Column(db.JSON, default=list)
    
    # Disassembly information
    disassembly_data = db.Column(db.JSON, default=dict)
    
    # Equipment stats (for weapons/armor)
    equipment_stats = db.Column(db.JSON, default=dict)
    
    # Requirements (attribute minimums, etc.)
    requirements = db.Column(db.JSON, default=dict)
    
    # Relationships
    items = db.relationship('Item', backref='template', lazy='dynamic')
    
    def __repr__(self):
        return f'<ItemTemplate {self.template_id}>'

class Item(db.Model):
    """Individual item instance"""
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('item_templates.id'), nullable=False)
    
    # Instance properties
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    condition = db.Column(db.Integer, default=100)  # 0-100%
    quality_modifier = db.Column(db.Float, default=1.0)  # Crafting quality
    
    # Component tracking
    components_used = db.Column(db.JSON, default=list)
    recipe_id = db.Column(db.String(100))  # How this item was crafted
    disassemble_yield = db.Column(db.JSON, default=dict)
    
    # Ownership and location
    owner_character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    equipped_character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    container_id = db.Column(db.Integer, db.ForeignKey('items.id'))  # For containers
    
    # Instance-specific modifications
    modifications = db.Column(db.JSON, default=dict)
    enchantments = db.Column(db.JSON, default=list)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('characters.id'))
    
    # Relationships
    contained_items = db.relationship('Item', backref=db.backref('container', remote_side=[id]), lazy='dynamic', foreign_keys=[container_id])
    
    def get_effective_stats(self):
        """Get stats with quality and condition modifiers applied"""
        if not self.template or not self.template.equipment_stats:
            return {}
        
        stats = self.template.equipment_stats.copy()
        condition_multiplier = self.condition / 100.0
        quality_multiplier = self.quality_modifier
        
        # Apply modifiers to numeric stats
        for key, value in stats.items():
            if isinstance(value, (int, float)):
                stats[key] = int(value * condition_multiplier * quality_multiplier)
        
        return stats
    
    def can_disassemble(self, character):
        """Check if character can disassemble this item"""
        if not self.template or not self.template.disassembly_data:
            return False, "This item cannot be disassembled"
        
        disassembly = self.template.disassembly_data
        skill_required = disassembly.get('skill_required')
        
        if skill_required:
            skill_name, min_level = skill_required.split(':')
            min_level = int(min_level)
            character_skill = character.skills.get(skill_name, 0)
            if character_skill < min_level:
                return False, f"Requires {skill_name} level {min_level}"
        
        return True, "Can disassemble"
    
    def get_disassembly_yield(self, character_skill_level=0):
        """Get what this item yields when disassembled"""
        if not self.template or not self.template.disassembly_data:
            return []
        
        disassembly = self.template.disassembly_data
        base_yield = disassembly.get('yields', [])
        
        # Apply skill-based yield improvements
        skill_bonus = min(character_skill_level * 0.1, 0.5)  # Max 50% bonus
        
        result = []
        for item_yield in base_yield:
            yield_item = item_yield.copy()
            if 'quantity' in yield_item:
                yield_item['quantity'] = max(1, int(yield_item['quantity'] * (1 + skill_bonus)))
            result.append(yield_item)
        
        return result
    
    def is_equipment(self):
        """Check if this is equipment (weapon/armor/accessory)"""
        if not self.template:
            return False
        base_type = self.template.base_type
        return base_type.startswith('weapon.') or base_type.startswith('armor.') or base_type.startswith('accessory.')
    
    def is_weapon(self):
        """Check if this is a weapon"""
        return self.template and self.template.base_type.startswith('weapon.')
    
    def is_armor(self):
        """Check if this is armor"""
        return self.template and self.template.base_type.startswith('armor.')
    
    def is_consumable(self):
        """Check if this is a consumable"""
        return self.template and self.template.base_type.startswith('consumable.')
    
    def is_container(self):
        """Check if this is a container"""
        return self.template and self.template.base_type == 'container'
    
    def __repr__(self):
        return f'<Item {self.name} (ID: {self.id})>'
