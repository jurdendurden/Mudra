"""
Item socketing system for gems and runes.
Handles adding/removing socketed items and calculating bonuses.
"""

from app.models.item_constants import SocketType, GemType, DamageType


class SocketingSystem:
    """Handles item socketing operations"""
    
    @staticmethod
    def can_socket_item(item, gem_item):
        """Check if a gem/rune can be socketed into an item"""
        if not item.template:
            return False, "Item has no template"
        
        if not item.sockets:
            return False, "Item has no sockets"
        
        # Check for empty socket
        empty_sockets = [s for s in item.sockets if not s.get('filled')]
        if not empty_sockets:
            return False, "No empty sockets available"
        
        # Check gem type compatibility
        if not gem_item.template:
            return False, "Gem has no template"
        
        # Find compatible socket
        gem_socket_type = SocketType.GEM.value  # Default
        if hasattr(gem_item.template, 'item_type'):
            from app.models.item_constants import ItemType
            if gem_item.template.item_type == ItemType.SOCKET_GEM:
                gem_socket_type = SocketType.GEM.value
            elif gem_item.template.item_type == ItemType.SOCKET_RUNE:
                gem_socket_type = SocketType.RUNE.value
        
        compatible_sockets = [s for s in empty_sockets if s.get('type') == gem_socket_type]
        if not compatible_sockets:
            return False, f"No compatible {gem_socket_type} sockets available"
        
        return True, "Can socket"
    
    @staticmethod
    def socket_gem(item, gem_item):
        """Socket a gem or rune into an item"""
        can_socket, message = SocketingSystem.can_socket_item(item, gem_item)
        if not can_socket:
            return False, message
        
        # Find first compatible empty socket
        gem_socket_type = SocketType.GEM.value
        if hasattr(gem_item.template, 'item_type'):
            from app.models.item_constants import ItemType
            if gem_item.template.item_type == ItemType.SOCKET_RUNE:
                gem_socket_type = SocketType.RUNE.value
        
        socket_index = None
        for i, socket in enumerate(item.sockets):
            if not socket.get('filled') and socket.get('type') == gem_socket_type:
                socket_index = i
                break
        
        if socket_index is None:
            return False, "No compatible socket found"
        
        # Socket the gem
        success, msg = item.socket_gem(socket_index, gem_item)
        return success, msg
    
    @staticmethod
    def unsocket_gem(item, socket_index, destroy_gem=False):
        """Remove a gem from a socket"""
        gem_id, message = item.remove_gem(socket_index, destroy_gem)
        return gem_id, message
    
    @staticmethod
    def get_socket_bonuses(item):
        """Calculate total bonuses from all socketed items"""
        if not item.sockets:
            return {}
        
        bonuses = {
            'damage_bonus': 0,
            'armor_bonus': 0,
            'damage_types': [],
            'resistances': {},
            'stats': {}
        }
        
        for socket in item.sockets:
            if not socket.get('filled'):
                continue
            
            socket_bonuses = socket.get('bonuses', {})
            
            # Add damage bonuses
            bonuses['damage_bonus'] += socket_bonuses.get('damage_bonus', 0)
            
            # Add armor bonuses
            bonuses['armor_bonus'] += socket_bonuses.get('armor_bonus', 0)
            
            # Add damage types
            if socket_bonuses.get('damage_type'):
                bonuses['damage_types'].append({
                    'type': socket_bonuses['damage_type'],
                    'min': socket_bonuses.get('damage_min', 0),
                    'max': socket_bonuses.get('damage_max', 0)
                })
            
            # Add resistances
            if socket_bonuses.get('damage_reduction'):
                for dmg_type, amount in socket_bonuses['damage_reduction'].items():
                    bonuses['resistances'][dmg_type] = bonuses['resistances'].get(dmg_type, 0) + amount
            
            # Add stat bonuses
            for stat in ['strength', 'agility', 'constitution', 'cognition', 'mystical', 'will']:
                if stat in socket_bonuses:
                    bonuses['stats'][stat] = bonuses['stats'].get(stat, 0) + socket_bonuses[stat]
        
        return bonuses


class GemBonusCalculator:
    """Calculates bonuses provided by different gem types"""
    
    # Gem type to bonus mapping
    GEM_BONUSES = {
        GemType.RUBY: {
            'damage_type': DamageType.FIRE.value,
            'damage_min': 3,
            'damage_max': 7,
            'damage_reduction': {DamageType.FIRE.value: 5}
        },
        GemType.SAPPHIRE: {
            'damage_type': DamageType.COLD.value,
            'damage_min': 3,
            'damage_max': 7,
            'damage_reduction': {DamageType.COLD.value: 5}
        },
        GemType.EMERALD: {
            'damage_type': DamageType.POISON.value,
            'damage_min': 2,
            'damage_max': 5,
            'damage_reduction': {DamageType.POISON.value: 5},
            'stats': {'constitution': 2}
        },
        GemType.DIAMOND: {
            'damage_type': DamageType.HOLY.value,
            'damage_min': 4,
            'damage_max': 8,
            'armor_bonus': 3,
            'damage_reduction': {DamageType.NEGATIVE.value: 8}
        },
        GemType.AMETHYST: {
            'damage_type': DamageType.ENERGY.value,
            'damage_min': 3,
            'damage_max': 6,
            'stats': {'mystical': 3}
        },
        GemType.TOPAZ: {
            'damage_type': DamageType.LIGHTNING.value,
            'damage_min': 2,
            'damage_max': 9,
            'damage_reduction': {DamageType.LIGHTNING.value: 5}
        },
        GemType.ONYX: {
            'damage_type': DamageType.NEGATIVE.value,
            'damage_min': 3,
            'damage_max': 7,
            'damage_reduction': {DamageType.HOLY.value: 5},
            'stats': {'will': 2}
        },
        GemType.PEARL: {
            'damage_type': DamageType.WATER.value,
            'damage_min': 2,
            'damage_max': 6,
            'damage_reduction': {DamageType.FIRE.value: 3, DamageType.LIGHTNING.value: 3}
        },
        GemType.CITRINE: {
            'damage_type': DamageType.EARTH.value,
            'damage_min': 3,
            'damage_max': 6,
            'armor_bonus': 2,
            'stats': {'strength': 2}
        },
        GemType.GARNET: {
            'damage_bonus': 4,
            'stats': {'strength': 1, 'constitution': 1}
        },
        GemType.OPAL: {
            'damage_bonus': 2,
            'armor_bonus': 2,
            'stats': {'mystical': 2, 'will': 1}
        },
        GemType.MOONSTONE: {
            'damage_type': DamageType.PSYCHIC.value,
            'damage_min': 2,
            'damage_max': 6,
            'stats': {'cognition': 3, 'mystical': 1}
        }
    }
    
    @staticmethod
    def get_gem_bonuses(gem_type, quality_modifier=1.0):
        """Get bonuses for a gem type with quality scaling"""
        if isinstance(gem_type, str):
            try:
                gem_type = GemType(gem_type)
            except ValueError:
                return {}
        
        base_bonuses = GemBonusCalculator.GEM_BONUSES.get(gem_type, {}).copy()
        
        # Scale bonuses by quality
        if quality_modifier != 1.0:
            for key, value in base_bonuses.items():
                if key in ['damage_min', 'damage_max', 'damage_bonus', 'armor_bonus']:
                    base_bonuses[key] = int(value * quality_modifier)
                elif key == 'stats':
                    for stat, amount in value.items():
                        base_bonuses[key][stat] = int(amount * quality_modifier)
                elif key == 'damage_reduction':
                    for dmg_type, amount in value.items():
                        base_bonuses[key][dmg_type] = int(amount * quality_modifier)
        
        return base_bonuses
    
    @staticmethod
    def create_gem_template_stats(gem_type, quality='common'):
        """Create equipment_stats for a gem template"""
        quality_multipliers = {
            'poor': 0.5,
            'common': 1.0,
            'good': 1.2,
            'uncommon': 1.5,
            'rare': 2.0,
            'epic': 2.5,
            'legendary': 3.0
        }
        
        multiplier = quality_multipliers.get(quality, 1.0)
        return GemBonusCalculator.get_gem_bonuses(gem_type, multiplier)

