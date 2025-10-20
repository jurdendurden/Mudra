from app import db
from datetime import datetime
import json
from app.models.item_constants import (
    ItemType, WeaponType, DamageType, MaterialType, 
    QualityTier, SocketType, WearFlag, ItemFlag, ItemFlag2,
    get_weapon_base_damage_type, get_weapon_base_speed,
    get_material_weight_modifier, get_material_durability_modifier
)

class ItemTemplate(db.Model):
    """Template for items - defines base properties"""
    __tablename__ = 'item_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Item type classification
    item_type = db.Column(db.Integer, nullable=False, default=ItemType.TRASH)  # ItemType enum
    base_type = db.Column(db.String(100), nullable=False)  # e.g., 'weapon.blade.sword'
    subtype = db.Column(db.String(100))
    
    # Base properties
    weight = db.Column(db.Float, default=0.0)
    value = db.Column(db.Integer, default=0)
    quality_tier = db.Column(db.String(20), default='common')  # QualityTier enum
    material = db.Column(db.String(50))  # MaterialType enum
    
    # Item flags (stored as JSON arrays of flag names)
    item_flags = db.Column(db.JSON, default=list)  # ItemFlag values
    item_flags_2 = db.Column(db.JSON, default=list)  # ItemFlag2 values
    wear_flags = db.Column(db.JSON, default=list)  # WearFlag values
    
    # Socket system
    socket_count = db.Column(db.Integer, default=0)  # Number of sockets
    socket_types = db.Column(db.JSON, default=list)  # Types of sockets [SocketType.GEM, SocketType.RUNE]
    
    # Weapon-specific properties
    weapon_type = db.Column(db.Integer)  # WeaponType enum
    weapon_flags = db.Column(db.JSON, default=list)  # WeaponFlag values
    base_damage_min = db.Column(db.Integer)
    base_damage_max = db.Column(db.Integer)
    attack_speed = db.Column(db.Float, default=1.0)  # Attacks per round modifier
    damage_types = db.Column(db.JSON, default=list)  # Primary and secondary damage types
    
    # Armor-specific properties
    armor_class = db.Column(db.Integer, default=0)
    armor_slot = db.Column(db.String(50))  # WearFlag value for primary slot
    damage_reduction = db.Column(db.JSON, default=dict)  # Reduction by damage type
    
    # Container properties
    container_capacity = db.Column(db.Integer, default=0)  # Max items
    container_weight_capacity = db.Column(db.Float, default=0.0)  # Max weight
    weight_reduction = db.Column(db.Float, default=0.0)  # % weight reduction for contents
    
    # Consumable properties
    consumable_charges = db.Column(db.Integer, default=1)
    consumable_effects = db.Column(db.JSON, default=list)  # Effect definitions
    
    # Component requirements for crafting
    components_required = db.Column(db.JSON, default=list)
    crafting_skill = db.Column(db.String(50))  # Required skill
    crafting_difficulty = db.Column(db.Integer, default=1)  # Minimum skill level
    
    # Disassembly information
    disassembly_data = db.Column(db.JSON, default=dict)
    
    # Equipment stats (for weapons/armor)
    equipment_stats = db.Column(db.JSON, default=dict)
    
    # Requirements (attribute minimums, etc.)
    requirements = db.Column(db.JSON, default=dict)
    
    # Durability
    max_durability = db.Column(db.Integer, default=100)
    
    # Enchantability
    max_enchantments = db.Column(db.Integer, default=0)  # How many enchantments can be applied
    enchantable = db.Column(db.Boolean, default=True)
    
    # Relationships
    items = db.relationship('Item', backref='template', lazy='dynamic')
    
    def get_effective_weight(self):
        """Calculate weight with material modifier"""
        if not self.material:
            return self.weight
        try:
            material_enum = MaterialType(self.material)
            modifier = get_material_weight_modifier(material_enum)
            return self.weight * modifier
        except (ValueError, KeyError):
            return self.weight
    
    def get_effective_durability(self):
        """Calculate durability with material modifier"""
        if not self.material:
            return self.max_durability
        try:
            material_enum = MaterialType(self.material)
            modifier = get_material_durability_modifier(material_enum)
            return int(self.max_durability * modifier)
        except (ValueError, KeyError):
            return self.max_durability
    
    def get_base_damage_type(self):
        """Get the primary damage type for this weapon"""
        if self.weapon_type is not None:
            try:
                weapon_enum = WeaponType(self.weapon_type)
                return get_weapon_base_damage_type(weapon_enum).value
            except ValueError:
                pass
        return DamageType.PHYSICAL.value
    
    def has_flag(self, flag):
        """Check if template has a specific flag"""
        if isinstance(flag, str):
            return flag in (self.item_flags or []) or flag in (self.item_flags_2 or [])
        return flag.value in (self.item_flags or []) or flag.value in (self.item_flags_2 or [])
    
    def can_wear_at(self, slot):
        """Check if item can be worn at a specific slot"""
        if isinstance(slot, str):
            return slot in (self.wear_flags or [])
        return slot.value in (self.wear_flags or [])
    
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
    current_durability = db.Column(db.Integer)  # Current durability points
    quality_modifier = db.Column(db.Float, default=1.0)  # Crafting quality (0.5-1.5)
    
    # Socket system - instances have sockets filled
    sockets = db.Column(db.JSON, default=list)  # List of socket dicts: [{type: 'gem', item_id: X, filled: True}]
    
    # Enchantment system - applied enchantments
    enchantments = db.Column(db.JSON, default=list)  # List of enchantment dicts
    
    # Weapon modifications
    sharpness = db.Column(db.Integer, default=0)  # +damage from sharpening
    balance = db.Column(db.Integer, default=0)  # +accuracy from balancing
    
    # Custom modifications from crafting/upgrading
    custom_name = db.Column(db.String(200))  # Custom name from crafting
    custom_flags = db.Column(db.JSON, default=list)  # Additional flags from enchanting
    
    # Component tracking
    components_used = db.Column(db.JSON, default=list)
    recipe_id = db.Column(db.String(100))  # How this item was crafted
    crafted_by_name = db.Column(db.String(100))  # Crafter's signature
    disassemble_yield = db.Column(db.JSON, default=dict)
    
    # Ownership and location
    owner_character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    equipped_character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    owner_npc_id = db.Column(db.Integer, db.ForeignKey('npcs.id'))
    equipped_npc_id = db.Column(db.Integer, db.ForeignKey('npcs.id'))
    equipped_slot = db.Column(db.String(50))  # Which slot it's equipped in
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    container_id = db.Column(db.Integer, db.ForeignKey('items.id'))  # For containers
    
    # Instance-specific modifications
    modifications = db.Column(db.JSON, default=dict)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('characters.id'))
    last_repaired_at = db.Column(db.DateTime)
    
    # Relationships
    contained_items = db.relationship('Item', backref=db.backref('container', remote_side=[id]), lazy='dynamic', foreign_keys=[container_id])
    
    def get_display_name(self):
        """Get the display name including custom name and quality"""
        if self.custom_name:
            return self.custom_name
        
        quality_prefix = ""
        if self.template and self.template.quality_tier:
            tier = self.template.quality_tier
            if tier == QualityTier.EPIC.value:
                quality_prefix = "Epic "
            elif tier == QualityTier.LEGENDARY.value:
                quality_prefix = "Legendary "
            elif tier == QualityTier.ARTIFACT.value:
                quality_prefix = "Artifact "
        
        return f"{quality_prefix}{self.name}"
    
    def get_effective_weight(self):
        """Get the effective weight including modifications"""
        if not self.template:
            return 0.0
        
        base_weight = self.template.get_effective_weight()
        
        # Container weight reduction
        if self.container_id:
            container = Item.query.get(self.container_id)
            if container and container.template:
                reduction = container.template.weight_reduction
                base_weight *= (1.0 - reduction)
        
        return base_weight
    
    def get_total_weight(self):
        """Get total weight including contained items"""
        weight = self.get_effective_weight()
        
        # Add weight of contained items
        if self.is_container():
            for item in self.contained_items:
                weight += item.get_effective_weight()
        
        return weight
    
    def initialize_sockets(self):
        """Initialize socket data based on template"""
        if not self.template or self.template.socket_count == 0:
            self.sockets = []
            return
        
        sockets = []
        socket_types = self.template.socket_types or []
        
        for i in range(self.template.socket_count):
            socket_type = socket_types[i] if i < len(socket_types) else SocketType.GEM.value
            sockets.append({
                'index': i,
                'type': socket_type,
                'filled': False,
                'item_id': None,
                'gem_type': None,
                'bonuses': {}
            })
        
        self.sockets = sockets
    
    def socket_gem(self, socket_index, gem_item):
        """Socket a gem into this item"""
        if not self.sockets or socket_index >= len(self.sockets):
            return False, "Invalid socket index"
        
        socket = self.sockets[socket_index]
        if socket['filled']:
            return False, "Socket already filled"
        
        # Extract gem bonuses
        gem_bonuses = gem_item.template.equipment_stats if gem_item.template else {}
        
        socket['filled'] = True
        socket['item_id'] = gem_item.id
        socket['gem_type'] = gem_item.template.subtype if gem_item.template else None
        socket['bonuses'] = gem_bonuses
        
        # Mark modified
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(self, 'sockets')
        
        return True, "Gem socketed successfully"
    
    def remove_gem(self, socket_index, destroy_gem=False):
        """Remove a gem from a socket"""
        if not self.sockets or socket_index >= len(self.sockets):
            return None, "Invalid socket index"
        
        socket = self.sockets[socket_index]
        if not socket['filled']:
            return None, "Socket is empty"
        
        gem_id = socket['item_id']
        
        # Clear socket
        socket['filled'] = False
        socket['item_id'] = None
        socket['gem_type'] = None
        socket['bonuses'] = {}
        
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(self, 'sockets')
        
        if destroy_gem:
            return None, "Gem destroyed"
        else:
            return gem_id, "Gem removed"
    
    def add_enchantment(self, enchantment_data):
        """Add an enchantment to this item"""
        if not self.template or not self.template.enchantable:
            return False, "Item cannot be enchanted"
        
        current_enchantments = self.enchantments or []
        max_enchantments = self.template.max_enchantments or 0
        
        if len(current_enchantments) >= max_enchantments:
            return False, f"Item can only hold {max_enchantments} enchantments"
        
        # Enchantment data structure:
        # {
        #     'name': 'Flaming',
        #     'type': 'damage',
        #     'damage_type': 'fire',
        #     'bonus_damage': [5, 10],
        #     'applied_by': 'Character Name',
        #     'applied_at': timestamp
        # }
        
        enchantment_data['applied_at'] = datetime.utcnow().isoformat()
        current_enchantments.append(enchantment_data)
        self.enchantments = current_enchantments
        
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(self, 'enchantments')
        
        return True, "Enchantment applied successfully"
    
    def get_effective_damage(self):
        """Calculate effective damage range with all modifiers"""
        if not self.template or not self.template.base_damage_min:
            return None, None
        
        min_dmg = self.template.base_damage_min
        max_dmg = self.template.base_damage_max or min_dmg
        
        # Apply quality modifier
        min_dmg = int(min_dmg * self.quality_modifier)
        max_dmg = int(max_dmg * self.quality_modifier)
        
        # Apply condition
        condition_mult = (self.condition / 100.0)
        min_dmg = int(min_dmg * condition_mult)
        max_dmg = int(max_dmg * condition_mult)
        
        # Apply sharpness
        if self.sharpness:
            min_dmg += self.sharpness
            max_dmg += self.sharpness
        
        # Apply socket bonuses
        if self.sockets:
            for socket in self.sockets:
                if socket.get('filled') and socket.get('bonuses'):
                    bonus_dmg = socket['bonuses'].get('damage_bonus', 0)
                    min_dmg += bonus_dmg
                    max_dmg += bonus_dmg
        
        # Apply enchantment bonuses
        if self.enchantments:
            for enchant in self.enchantments:
                if enchant.get('type') == 'damage':
                    bonus = enchant.get('flat_bonus', 0)
                    min_dmg += bonus
                    max_dmg += bonus
        
        return max(1, min_dmg), max(1, max_dmg)
    
    def get_damage_types(self):
        """Get all damage types this weapon deals"""
        if not self.is_weapon():
            return []
        
        damage_types = []
        
        # Base damage type from weapon
        if self.template:
            base_type = self.template.get_base_damage_type()
            damage_types.append({
                'type': base_type,
                'percentage': 100
            })
        
        # Additional damage from enchantments
        if self.enchantments:
            for enchant in self.enchantments:
                if enchant.get('type') == 'damage' and enchant.get('damage_type'):
                    damage_types.append({
                        'type': enchant['damage_type'],
                        'min': enchant.get('bonus_damage', [0, 0])[0],
                        'max': enchant.get('bonus_damage', [0, 0])[1]
                    })
        
        # Additional damage from sockets
        if self.sockets:
            for socket in self.sockets:
                if socket.get('filled') and socket.get('bonuses'):
                    dmg_type = socket['bonuses'].get('damage_type')
                    if dmg_type:
                        damage_types.append({
                            'type': dmg_type,
                            'min': socket['bonuses'].get('damage_min', 0),
                            'max': socket['bonuses'].get('damage_max', 0)
                        })
        
        return damage_types
    
    def get_attack_speed(self):
        """Get effective attack speed"""
        if not self.is_weapon() or not self.template:
            return 1.0
        
        base_speed = self.template.attack_speed or 1.0
        
        # Balance improvements
        if self.balance:
            base_speed *= (1.0 - (self.balance * 0.01))  # 1% faster per balance point
        
        # Enchantment modifiers
        if self.enchantments:
            for enchant in self.enchantments:
                if enchant.get('type') == 'speed':
                    base_speed *= enchant.get('multiplier', 1.0)
        
        return base_speed
    
    def get_armor_class(self):
        """Get effective armor class"""
        if not self.template:
            return 0
        
        base_ac = self.template.armor_class or 0
        
        # Apply quality
        base_ac = int(base_ac * self.quality_modifier)
        
        # Apply condition
        base_ac = int(base_ac * (self.condition / 100.0))
        
        # Socket bonuses
        if self.sockets:
            for socket in self.sockets:
                if socket.get('filled') and socket.get('bonuses'):
                    base_ac += socket['bonuses'].get('armor_bonus', 0)
        
        # Enchantment bonuses
        if self.enchantments:
            for enchant in self.enchantments:
                if enchant.get('type') == 'armor':
                    base_ac += enchant.get('armor_bonus', 0)
        
        return base_ac
    
    def get_damage_reduction(self):
        """Get damage reduction by type"""
        if not self.template:
            return {}
        
        reduction = (self.template.damage_reduction or {}).copy()
        
        # Add reductions from sockets
        if self.sockets:
            for socket in self.sockets:
                if socket.get('filled') and socket.get('bonuses'):
                    socket_reduction = socket['bonuses'].get('damage_reduction', {})
                    for dmg_type, amount in socket_reduction.items():
                        reduction[dmg_type] = reduction.get(dmg_type, 0) + amount
        
        # Add reductions from enchantments
        if self.enchantments:
            for enchant in self.enchantments:
                if enchant.get('type') == 'resistance':
                    dmg_type = enchant.get('damage_type')
                    amount = enchant.get('reduction', 0)
                    if dmg_type:
                        reduction[dmg_type] = reduction.get(dmg_type, 0) + amount
        
        return reduction
    
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
        
        # Add comprehensive calculated stats
        if self.is_weapon():
            min_dmg, max_dmg = self.get_effective_damage()
            if min_dmg:
                stats['damage'] = [min_dmg, max_dmg]
            stats['attack_speed'] = self.get_attack_speed()
            stats['damage_types'] = self.get_damage_types()
        
        if self.is_armor():
            stats['armor_class'] = self.get_armor_class()
            stats['damage_reduction'] = self.get_damage_reduction()
        
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
        
        # Add gems from sockets if item is being destroyed
        if self.sockets:
            for socket in self.sockets:
                if socket.get('filled') and socket.get('item_id'):
                    result.append({
                        'type': 'existing_item',
                        'item_id': socket['item_id'],
                        'quantity': 1
                    })
        
        return result
    
    def damage_item(self, amount=1):
        """Damage the item, reducing durability"""
        if not self.template:
            return
        
        max_dur = self.template.get_effective_durability()
        if self.current_durability is None:
            self.current_durability = max_dur
        
        self.current_durability = max(0, self.current_durability - amount)
        self.condition = int((self.current_durability / max_dur) * 100) if max_dur > 0 else 0
        
        # Check for item breaking
        if self.current_durability <= 0:
            return True  # Item broken
        
        return False
    
    def repair_item(self, amount=None):
        """Repair the item"""
        if not self.template:
            return
        
        max_dur = self.template.get_effective_durability()
        if self.current_durability is None:
            self.current_durability = max_dur
        
        if amount is None:
            # Full repair
            self.current_durability = max_dur
        else:
            self.current_durability = min(max_dur, self.current_durability + amount)
        
        self.condition = int((self.current_durability / max_dur) * 100) if max_dur > 0 else 100
        self.last_repaired_at = datetime.utcnow()
    
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
        return self.template and (
            self.template.base_type == 'container' or 
            self.template.item_type == ItemType.CONTAINER
        )
    
    def is_key(self):
        """Check if this is a key"""
        return self.template and self.template.base_type == 'key'
    
    def can_unlock_door(self, door_data):
        """Check if this key can unlock a specific door"""
        if not self.is_key() or not door_data:
            return False
        
        # Keys match doors by template_id
        required_key_id = door_data.get('key_id')
        if not required_key_id:
            return False
        
        # Match by template_id from the template
        return self.template.template_id == required_key_id
    
    def __repr__(self):
        return f'<Item {self.name} (ID: {self.id})>'
