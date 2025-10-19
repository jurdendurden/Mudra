# Item Templates - Organized by Category

This directory contains all item templates for the Mudra MUD, organized into logical category files for easier management and navigation.

## Quick Start

Each JSON file contains item templates grouped by functionality:

```python
# Example: Load weapon templates
import json

with open('data/items/weapons.json', 'r') as f:
    weapon_templates = json.load(f)

# Access a specific weapon
longsword = weapon_templates['mithril_longsword']
print(longsword['name'])  # "Mithril Longsword"
```

## File Organization

### Core Combat Items
- **weapons.json** - 13 weapons covering all weapon types (swords, axes, bows, etc.)
- **armor.json** - 9 armor pieces (helmets, chainmail, shields, boots, etc.)
- **ammunition.json** - 4 types of arrows and bolts

### Magical & Enhancement Items
- **gems.json** - 12 socketable gems and runes (ruby, diamond, amethyst, power runes, etc.)
- **magical_items.json** - 7 magical items (scrolls, wands, staffs, tomes)

### Containers & Storage
- **containers.json** - 5 containers (backpacks, satchels, quivers, sheaths)

### Consumables
- **consumables.json** - 10 consumable items (potions, pills, food, drink, bandages, salves)

### Crafting System
- **crafting_materials.json** - 14 raw materials (ingots, wood, leather, essences, herbs)
- **tools.json** - 12 crafting and gathering tools (hammers, pickaxes, saws, etc.)
- **crafting_stations.json** - 5 crafting stations (anvil, loom, stove, alchemy lab, workbench)
- **cooking_items.json** - 9 cooking utensils (skillets, pans, pots, etc.)
- **recipes.json** - 4 crafting recipes (alchemy, cooking, smithing, tailoring)

### Other Categories
- **clothing.json** - 6 non-armor clothing items (shirts, robes, cloaks)
- **furniture.json** - 4 furniture items (chairs, tables, beds)
- **special_items.json** - 30+ utility items (lights, keys, maps, instruments, etc.)
- **misc_items.json** - 16 miscellaneous items (corpses, structures, jewelry, dyes)

## Complete Coverage

**97 out of 101 item types** are covered with working examples:
- 4 slots are intentionally unused (types 14, 34, 66, 90) - reserved for future expansion
- 2 types are deprecated (types 81, 82)
- All other types have at least one functional example

See **ITEM_INDEX.md** for a complete mapping of item types to files.

## Item Template Structure

Each item template follows this structure:

```json
{
  "template_id": "unique_identifier",
  "name": "Display Name",
  "description": "Detailed description",
  "item_type": 5,
  "base_type": "weapon.blade.sword",
  "subtype": "longsword",
  "weight": 3.0,
  "value": 2500,
  "quality_tier": "rare",
  "material": "mithril",
  
  "item_flags": ["magic", "glow"],
  "wear_flags": ["take", "wield"],
  
  "socket_count": 2,
  "socket_types": ["gem", "gem"],
  
  "weapon_type": 11,
  "base_damage_min": 15,
  "base_damage_max": 25,
  "attack_speed": 1.0,
  "damage_types": ["slashing"],
  
  "max_durability": 180,
  "max_enchantments": 2,
  "enchantable": true,
  
  "crafting_skill": "smithing",
  "crafting_difficulty": 25,
  "components_required": [...],
  
  "requirements": {
    "strength": 15,
    "cognition": 8
  }
}
```

## Key Features Demonstrated

### Socketing System
Items like `mithril_longsword` show gem socket configuration:
```json
"socket_count": 2,
"socket_types": ["gem", "gem"]
```

Gems provide bonuses when socketed:
```json
"equipment_stats": {
  "damage_type": "fire",
  "damage_min": 5,
  "damage_max": 12
}
```

### Damage Types
Weapons support multiple damage types:
```json
"damage_types": ["slashing", "fire"]
```

### Material System
Materials affect weight and durability:
```json
"material": "mithril"  // Lighter, more durable than iron
```

### Enchanting
Items can be enchanted:
```json
"max_enchantments": 2,
"enchantable": true
```

### Quality Tiers
Items range from junk to mythic:
```json
"quality_tier": "legendary"
```

### Crafting & Deconstruction
Items specify components needed:
```json
"components_required": [
  {"type": "metal.mithril_ingot", "quantity": 4},
  {"type": "wood.ironwood", "quantity": 1}
],
"disassembly_data": {
  "skill_required": "smithing:20",
  "yields": [...]
}
```

## Adding New Items

1. Choose the appropriate category file
2. Add a new entry with a unique `template_id`
3. Set the correct `item_type` from the ItemType enum
4. Configure properties based on item category
5. Add crafting/disassembly data if applicable

Example:
```json
"steel_dagger": {
  "template_id": "steel_dagger",
  "name": "Steel Dagger",
  "item_type": 5,
  "weapon_type": 1,
  "base_damage_min": 6,
  "base_damage_max": 10,
  "attack_speed": 0.8,
  ...
}
```

## Integration with Game Systems

These templates integrate with:
- **Combat System** - Damage calculations, weapon speeds, armor class
- **Crafting System** - Component requirements, skill levels
- **Socket System** - Gem/rune insertion and bonuses
- **Enchanting System** - Magical enhancements
- **Economy System** - Item values and trading
- **Inventory System** - Weight, containers, equipment slots

## Statistics

- **Total Templates**: 150+
- **Total Files**: 16 category files + 2 documentation files
- **Coverage**: 97/101 item types (95.0%)
- **Examples per Type**: 1-13 depending on category

## Documentation

- **ITEM_INDEX.md** - Complete type-to-file mapping
- **README.md** - This file
- See `documentation/item_system.md` for technical details on the item system implementation

## Notes

- All items use snake_case for IDs
- Values are in copper pieces (base currency)
- Weight is in pounds
- Durability represents item condition (0-max)
- Attack speed: lower = faster (daggers ~0.7, greatswords ~1.5)
- Socket types: "gem", "rune", or "enchant"

## Migration from comprehensive_templates.json

The original monolithic `comprehensive_templates.json` file has been split into these 16 organized category files. All original items have been preserved and 100+ new examples have been added to ensure complete coverage of all item types.

