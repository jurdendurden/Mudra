"""
Item enchanting system.
Handles applying enchantments and calculating their effects.
"""

from datetime import datetime
from app.models.item_constants import DamageType, WeaponFlag


class EnchantingSystem:
    """Handles item enchanting operations"""
    
    # Available enchantments
    WEAPON_ENCHANTMENTS = {
        'flaming': {
            'name': 'Flaming',
            'type': 'damage',
            'damage_type': DamageType.FIRE.value,
            'bonus_damage': [5, 10],
            'skill_required': 'enchanting',
            'skill_level': 10,
            'materials': [
                {'type': 'essence.fire', 'quantity': 5},
                {'type': 'gem.ruby', 'quantity': 1}
            ]
        },
        'frost': {
            'name': 'Frost',
            'type': 'damage',
            'damage_type': DamageType.COLD.value,
            'bonus_damage': [4, 9],
            'skill_required': 'enchanting',
            'skill_level': 10,
            'materials': [
                {'type': 'essence.cold', 'quantity': 5},
                {'type': 'gem.sapphire', 'quantity': 1}
            ]
        },
        'shocking': {
            'name': 'Shocking',
            'type': 'damage',
            'damage_type': DamageType.LIGHTNING.value,
            'bonus_damage': [3, 12],
            'skill_required': 'enchanting',
            'skill_level': 12,
            'materials': [
                {'type': 'essence.lightning', 'quantity': 5},
                {'type': 'gem.topaz', 'quantity': 1}
            ]
        },
        'vampiric': {
            'name': 'Vampiric',
            'type': 'special',
            'effect': 'lifesteal',
            'lifesteal_percent': 10,
            'skill_required': 'enchanting',
            'skill_level': 15,
            'materials': [
                {'type': 'essence.blood', 'quantity': 10},
                {'type': 'gem.garnet', 'quantity': 2}
            ]
        },
        'holy': {
            'name': 'Holy',
            'type': 'damage',
            'damage_type': DamageType.HOLY.value,
            'bonus_damage': [6, 12],
            'effective_against': ['undead', 'demon'],
            'skill_required': 'enchanting',
            'skill_level': 18,
            'materials': [
                {'type': 'essence.holy', 'quantity': 10},
                {'type': 'gem.diamond', 'quantity': 1}
            ]
        },
        'vorpal': {
            'name': 'Vorpal',
            'type': 'special',
            'effect': 'critical',
            'critical_chance': 10,
            'critical_multiplier': 1.5,
            'skill_required': 'enchanting',
            'skill_level': 20,
            'materials': [
                {'type': 'essence.death', 'quantity': 15},
                {'type': 'gem.diamond', 'quantity': 2}
            ]
        },
        'sharpness': {
            'name': 'Sharpness',
            'type': 'damage',
            'flat_bonus': 5,
            'skill_required': 'enchanting',
            'skill_level': 5,
            'materials': [
                {'type': 'essence.arcane', 'quantity': 3},
                {'type': 'component.whetstone', 'quantity': 1}
            ]
        },
        'swiftness': {
            'name': 'Swiftness',
            'type': 'speed',
            'multiplier': 0.9,  # 10% faster attacks
            'skill_required': 'enchanting',
            'skill_level': 12,
            'materials': [
                {'type': 'essence.air', 'quantity': 8},
                {'type': 'gem.opal', 'quantity': 1}
            ]
        }
    }
    
    ARMOR_ENCHANTMENTS = {
        'protection': {
            'name': 'Protection',
            'type': 'armor',
            'armor_bonus': 5,
            'skill_required': 'enchanting',
            'skill_level': 8,
            'materials': [
                {'type': 'essence.arcane', 'quantity': 5},
                {'type': 'gem.diamond', 'quantity': 1}
            ]
        },
        'fire_resistance': {
            'name': 'Fire Resistance',
            'type': 'resistance',
            'damage_type': DamageType.FIRE.value,
            'reduction': 15,
            'skill_required': 'enchanting',
            'skill_level': 10,
            'materials': [
                {'type': 'essence.fire', 'quantity': 5},
                {'type': 'gem.ruby', 'quantity': 1}
            ]
        },
        'cold_resistance': {
            'name': 'Cold Resistance',
            'type': 'resistance',
            'damage_type': DamageType.COLD.value,
            'reduction': 15,
            'skill_required': 'enchanting',
            'skill_level': 10,
            'materials': [
                {'type': 'essence.cold', 'quantity': 5},
                {'type': 'gem.sapphire', 'quantity': 1}
            ]
        },
        'lightning_resistance': {
            'name': 'Lightning Resistance',
            'type': 'resistance',
            'damage_type': DamageType.LIGHTNING.value,
            'reduction': 15,
            'skill_required': 'enchanting',
            'skill_level': 10,
            'materials': [
                {'type': 'essence.lightning', 'quantity': 5},
                {'type': 'gem.topaz', 'quantity': 1}
            ]
        },
        'fortitude': {
            'name': 'Fortitude',
            'type': 'stats',
            'stat_bonuses': {'constitution': 3, 'strength': 2},
            'skill_required': 'enchanting',
            'skill_level': 15,
            'materials': [
                {'type': 'essence.earth', 'quantity': 10},
                {'type': 'gem.citrine', 'quantity': 2}
            ]
        },
        'vitality': {
            'name': 'Vitality',
            'type': 'stats',
            'stat_bonuses': {'constitution': 5},
            'max_health_bonus': 20,
            'skill_required': 'enchanting',
            'skill_level': 12,
            'materials': [
                {'type': 'essence.life', 'quantity': 8},
                {'type': 'gem.emerald', 'quantity': 1}
            ]
        },
        'warding': {
            'name': 'Warding',
            'type': 'resistance',
            'damage_type': DamageType.ENERGY.value,
            'reduction': 10,
            'armor_bonus': 3,
            'skill_required': 'enchanting',
            'skill_level': 18,
            'materials': [
                {'type': 'essence.arcane', 'quantity': 12},
                {'type': 'gem.amethyst', 'quantity': 2}
            ]
        }
    }
    
    @staticmethod
    def can_enchant_item(item, enchantment_key, character=None):
        """Check if an enchantment can be applied to an item"""
        if not item.template or not item.template.enchantable:
            return False, "Item cannot be enchanted"
        
        # Get enchantment definition
        enchantment = None
        if item.is_weapon():
            enchantment = EnchantingSystem.WEAPON_ENCHANTMENTS.get(enchantment_key)
        elif item.is_armor():
            enchantment = EnchantingSystem.ARMOR_ENCHANTMENTS.get(enchantment_key)
        
        if not enchantment:
            return False, "Unknown enchantment"
        
        # Check if item is weapon/armor type
        if enchantment_key in EnchantingSystem.WEAPON_ENCHANTMENTS and not item.is_weapon():
            return False, "This enchantment can only be applied to weapons"
        
        if enchantment_key in EnchantingSystem.ARMOR_ENCHANTMENTS and not item.is_armor():
            return False, "This enchantment can only be applied to armor"
        
        # Check enchantment slots
        current_enchantments = item.enchantments or []
        max_enchantments = item.template.max_enchantments or 0
        
        if len(current_enchantments) >= max_enchantments:
            return False, f"Item can only hold {max_enchantments} enchantments"
        
        # Check for duplicate enchantments
        existing_names = [e.get('name') for e in current_enchantments]
        if enchantment['name'] in existing_names:
            return False, "This enchantment is already applied"
        
        # Check skill requirements
        if character and enchantment.get('skill_required'):
            skill_name = enchantment['skill_required']
            skill_level = enchantment.get('skill_level', 1)
            
            character_skill = getattr(character, skill_name, 0) if hasattr(character, skill_name) else 0
            if character_skill < skill_level:
                return False, f"Requires {skill_name} level {skill_level}"
        
        return True, "Can enchant"
    
    @staticmethod
    def enchant_item(item, enchantment_key, character_name=None):
        """Apply an enchantment to an item"""
        can_enchant, message = EnchantingSystem.can_enchant_item(item, enchantment_key)
        if not can_enchant:
            return False, message
        
        # Get enchantment definition
        enchantment_def = None
        if item.is_weapon():
            enchantment_def = EnchantingSystem.WEAPON_ENCHANTMENTS.get(enchantment_key)
        elif item.is_armor():
            enchantment_def = EnchantingSystem.ARMOR_ENCHANTMENTS.get(enchantment_key)
        
        if not enchantment_def:
            return False, "Unknown enchantment"
        
        # Create enchantment data
        enchantment_data = {
            'id': enchantment_key,
            'name': enchantment_def['name'],
            'type': enchantment_def['type'],
            'applied_by': character_name
        }
        
        # Copy relevant properties
        for key in ['damage_type', 'bonus_damage', 'flat_bonus', 'armor_bonus', 
                    'reduction', 'stat_bonuses', 'effect', 'lifesteal_percent',
                    'critical_chance', 'critical_multiplier', 'multiplier',
                    'max_health_bonus', 'effective_against']:
            if key in enchantment_def:
                enchantment_data[key] = enchantment_def[key]
        
        # Apply enchantment
        success, msg = item.add_enchantment(enchantment_data)
        return success, msg
    
    @staticmethod
    def get_enchantment_materials(enchantment_key, is_weapon=True):
        """Get the materials required for an enchantment"""
        enchantments = EnchantingSystem.WEAPON_ENCHANTMENTS if is_weapon else EnchantingSystem.ARMOR_ENCHANTMENTS
        enchantment = enchantments.get(enchantment_key, {})
        return enchantment.get('materials', [])
    
    @staticmethod
    def calculate_enchantment_power(item):
        """Calculate total enchantment power/value"""
        if not item.enchantments:
            return 0
        
        power = 0
        for enchant in item.enchantments:
            # Base power from type
            if enchant.get('type') == 'damage':
                bonus_dmg = enchant.get('bonus_damage', [0, 0])
                power += (bonus_dmg[0] + bonus_dmg[1]) / 2
                power += enchant.get('flat_bonus', 0)
            elif enchant.get('type') == 'armor':
                power += enchant.get('armor_bonus', 0) * 2
            elif enchant.get('type') == 'resistance':
                power += enchant.get('reduction', 0)
            elif enchant.get('type') == 'speed':
                multiplier = enchant.get('multiplier', 1.0)
                power += (1.0 - multiplier) * 50  # Speed bonus worth a lot
            elif enchant.get('type') == 'special':
                power += 20  # Special effects worth flat amount
        
        return int(power)

