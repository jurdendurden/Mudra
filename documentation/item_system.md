# Item System Documentation

## Overview

The Mudra item system is a comprehensive implementation inspired by classic MUD design, featuring:
- 101+ item types from weapons to crafting materials
- Socket system for gems and runes
- Enchanting system with damage types
- Material-based modifiers for weight and durability
- Weapon speeds and damage type calculations
- Weight and encumbrance system
- Quality tiers from poor to mythic
- Full crafting and deconstruction support

## Item Types

The system supports 101 distinct item types based on traditional MUD classifications:

### Combat Items
- **Weapons** (5): Swords, daggers, axes, bows, staffs, etc.
- **Armor** (9): Various armor pieces
- **Shield** (wear flag): Defensive equipment
- **Missiles** (47): Arrows, bolts, thrown weapons

### Magical Items
- **Scrolls** (2): One-time spell casts
- **Wands** (3): Multi-charge spell items
- **Staffs** (4): Powerful magical weapons
- **Potions** (10): Consumable effects
- **Pills** (26): Quick consumables

### Containers
- **Container** (15): Bags, backpacks, chests
- **Quiver** (76): Arrow storage
- **Sheath** (67): Weapon storage

### Gems and Sockets
- **Gem** (32): Precious stones
- **Socket Gem** (85): Socketable gems
- **Socket Rune** (86): Socketable runes
- **Jewelry** (33): Rings, amulets

### Crafting Materials
- **Ingredient** (63): General crafting materials
- **Herb** (42): Alchemy ingredients
- **Skin** (37): Leather materials
- **Component**: Metal ingots, wood planks, etc.

### Tools
- **Blacksmith Hammer** (55): Smithing tool
- **Mining Tool** (43): Mining
- **Fish Pole** (44): Fishing
- **Thieves Tools** (39): Lock picking
- **Shears** (6): Cloth cutting
- **File/Lapidary** (7, 21): Gem cutting
- **Shovel** (64): Digging
- And many more...

### Crafting Stations
- **Anvil** (50): Blacksmithing
- **Loom** (51): Tailoring
- **Stove** (27): Cooking
- **Alchemy Lab** (46): Alchemy
- **Workbench** (74): General crafting
- **Mortar & Pestle** (75): Herbalism

## Socket System

Items can have sockets that accept gems or runes for additional bonuses.

### Socket Types
- **Gem Sockets**: Accept gem items that provide stat bonuses
- **Rune Sockets**: Accept rune items for special effects
- **Enchant Sockets**: Reserved for enchantments

### Socket Mechanics

```python
# Initialize sockets when creating an item
item.initialize_sockets()

# Socket a gem
success, message = item.socket_gem(socket_index, gem_item)

# Remove a gem (optionally destroying it)
gem_id, message = item.remove_gem(socket_index, destroy_gem=False)

# Get all socket bonuses
bonuses = SocketingSystem.get_socket_bonuses(item)
```

### Gem Types and Bonuses

| Gem Type | Damage Type | Bonus Damage | Resistance | Stats |
|----------|-------------|--------------|------------|-------|
| Ruby | Fire | 3-7 | Fire +5 | - |
| Sapphire | Cold | 3-7 | Cold +5 | - |
| Emerald | Poison | 2-5 | Poison +5 | CON +2 |
| Diamond | Holy | 4-8 | Negative +8 | Armor +3 |
| Amethyst | Energy | 3-6 | Energy +6 | MYS +3 |
| Topaz | Lightning | 2-9 | Lightning +5 | - |
| Onyx | Negative | 3-7 | Holy +5 | WIL +2 |
| Pearl | Water | 2-6 | Fire +3, Lightning +3 | - |
| Citrine | Earth | 3-6 | - | STR +2, Armor +2 |
| Garnet | - | +4 damage | - | STR +1, CON +1 |
| Opal | - | +2 damage | - | MYS +2, WIL +1, Armor +2 |
| Moonstone | Psychic | 2-6 | - | COG +3, MYS +1 |

## Enchanting System

Items can be enchanted to add special properties. The number of enchantments is limited by the item's `max_enchantments` value.

### Weapon Enchantments

| Enchantment | Type | Effect | Skill Level |
|-------------|------|--------|-------------|
| Flaming | Damage | +5-10 fire damage | 10 |
| Frost | Damage | +4-9 cold damage | 10 |
| Shocking | Damage | +3-12 lightning damage | 12 |
| Vampiric | Special | 10% lifesteal | 15 |
| Holy | Damage | +6-12 holy damage vs undead/demons | 18 |
| Vorpal | Special | +10% crit chance, 1.5x crit multiplier | 20 |
| Sharpness | Damage | +5 flat damage | 5 |
| Swiftness | Speed | 10% faster attacks | 12 |

### Armor Enchantments

| Enchantment | Type | Effect | Skill Level |
|-------------|------|--------|-------------|
| Protection | Armor | +5 armor class | 8 |
| Fire Resistance | Resistance | -15 fire damage | 10 |
| Cold Resistance | Resistance | -15 cold damage | 10 |
| Lightning Resistance | Resistance | -15 lightning damage | 10 |
| Fortitude | Stats | +3 CON, +2 STR | 15 |
| Vitality | Stats | +5 CON, +20 max HP | 12 |
| Warding | Mixed | +3 armor, -10 energy damage | 18 |

### Enchanting Example

```python
from app.systems.item_enchanting import EnchantingSystem

# Check if enchantment can be applied
can_enchant, message = EnchantingSystem.can_enchant_item(
    item, 
    'flaming', 
    character
)

# Apply enchantment
if can_enchant:
    success, msg = EnchantingSystem.enchant_item(
        item,
        'flaming',
        character_name=character.name
    )
```

## Damage Types

The system supports 18 distinct damage types:

### Physical Damage
- **Physical**: Generic physical damage
- **Slashing**: Swords, axes
- **Piercing**: Daggers, arrows, spears
- **Bludgeoning**: Maces, hammers, clubs

### Elemental Damage
- **Fire**: Flames and heat
- **Cold**: Ice and frost
- **Lightning**: Electrical damage
- **Acid**: Corrosive damage
- **Water**: Water-based attacks
- **Air**: Wind and air
- **Earth**: Stone and earth

### Magical Damage
- **Light**: Radiant energy
- **Negative**: Necromantic energy
- **Holy**: Divine power
- **Energy**: Pure arcane magic
- **Psychic**: Mental attacks
- **Sonic**: Sound-based damage
- **Poison**: Toxic damage

## Weapon Properties

### Weapon Types
Each weapon type has different base characteristics:

| Weapon Type | Base Speed | Primary Damage Type |
|-------------|-----------|---------------------|
| Dagger | 0.8 | Piercing |
| Short Sword | 1.0 | Slashing |
| Long Sword | 1.2 | Slashing |
| Mace | 1.1 | Bludgeoning |
| Axe | 1.3 | Slashing |
| Flail | 1.4 | Bludgeoning |
| Whip | 0.9 | Slashing |
| Spear | 1.1 | Piercing |
| Polearm | 1.5 | Piercing |
| Bow | 1.2 | Piercing |
| Crossbow | 1.6 | Piercing |
| Staff | 1.3 | Bludgeoning |
| Fist Weapon | 0.7 | Bludgeoning |

### Damage Calculation

```python
# Get effective damage with all modifiers
min_dmg, max_dmg = item.get_effective_damage()

# Factors that affect damage:
# - Base damage from template
# - Quality modifier (0.5 - 1.5)
# - Condition (0-100%)
# - Sharpness bonus
# - Socket bonuses
# - Enchantment bonuses

# Get all damage types
damage_types = item.get_damage_types()
# Returns: [
#   {'type': 'slashing', 'percentage': 100},
#   {'type': 'fire', 'min': 5, 'max': 10}
# ]
```

### Attack Speed

Attack speed determines how fast a weapon strikes:

```python
speed = item.get_attack_speed()

# Factors:
# - Base weapon speed (from weapon type)
# - Balance improvements (1% per point)
# - Enchantment modifiers
```

## Material System

Items can be crafted from different materials that affect weight and durability.

### Metal Materials
| Material | Weight Mod | Durability Mod |
|----------|-----------|----------------|
| Iron | 1.0 | 1.0 |
| Steel | 1.1 | 1.3 |
| Bronze | 1.2 | 0.9 |
| Copper | 0.9 | 0.7 |
| Silver | 1.05 | 0.8 |
| Gold | 1.9 | 0.6 |
| Mithril | 0.5 | 1.8 |
| Adamantine | 0.8 | 2.5 |
| Darksteel | 1.3 | 2.0 |

### Wood Materials
| Material | Weight Mod | Durability Mod |
|----------|-----------|----------------|
| Oak | 0.5 | 0.8 |
| Pine | 0.4 | 0.6 |
| Maple | 0.5 | 0.7 |
| Ash | 0.45 | 0.75 |
| Ebony | 0.7 | 1.0 |
| Ironwood | 0.8 | 1.2 |
| Yew | 0.4 | 0.7 |

### Fabric Materials
| Material | Weight Mod | Durability Mod |
|----------|-----------|----------------|
| Cotton | 0.1 | 0.3 |
| Linen | 0.1 | 0.4 |
| Wool | 0.15 | 0.4 |
| Silk | 0.05 | 0.5 |
| Leather | 0.3 | 0.6 |
| Hide | 0.4 | 0.7 |
| Scales | 0.6 | 1.1 |
| Dragonhide | 0.5 | 1.5 |

## Weight and Encumbrance

### Weight Calculation

```python
# Item effective weight with material modifier
effective_weight = item.get_effective_weight()

# Total weight including contents (for containers)
total_weight = item.get_total_weight()
```

### Container Weight Reduction

Containers can reduce the weight of items stored within them:

```python
# A backpack with 30% weight reduction
backpack.template.weight_reduction = 0.3

# Items inside weigh 70% of normal
```

## Item Flags

Items can have various flags that modify their behavior:

### Primary Flags (ItemFlag)
- `glow`: Emits light
- `hum`: Makes humming sound
- `magic`: Magical item
- `cursed`: Cannot be removed once equipped
- `blessed`: Holy item
- `invis`: Invisible
- `nodrop`: Cannot be dropped
- `noremove`: Cannot be removed
- `burn_proof`: Immune to fire
- `indestructible`: Cannot be destroyed

### Secondary Flags (ItemFlag2)
- `hidden`: Hidden from casual view
- `epic`: Epic quality
- `legendary`: Legendary quality
- `artifact`: Artifact quality
- `quest_item`: Quest-related item
- `unique`: Only one can exist
- `waterproof`: Immune to water damage
- `rusted`: Degraded condition

## Wear Positions

Items can be equipped in various slots:

- `finger`: Rings (2 slots)
- `neck`: Amulets, necklaces
- `chest`: Chest armor
- `head`: Helmets, hats
- `legs`: Leg armor
- `feet`: Boots, shoes
- `hands`: Gloves, gauntlets
- `arms`: Arm guards
- `shield`: Shields
- `shoulders`: Cloaks, pauldrons
- `waist`: Belts
- `wrist`: Bracers
- `wield`: Wielded weapons
- `hold`: Held items
- `ear`: Earrings
- `sheath`: Sheathed weapons
- `quiver`: Arrow containers
- `two_handed`: Two-handed weapons

## Quality Tiers

Items have quality tiers that affect their stats and value:

1. **Junk**: Broken, nearly worthless
2. **Poor**: Low quality, -20% stats
3. **Common**: Standard quality
4. **Good**: Above average, +10% stats
5. **Uncommon**: Enhanced, +20% stats
6. **Rare**: Exceptional, +40% stats
7. **Epic**: Masterwork, +60% stats
8. **Legendary**: Legendary, +100% stats
9. **Artifact**: Unique artifacts, +150% stats
10. **Mythic**: Divine items, +200% stats

## Durability System

Items have durability that degrades with use:

```python
# Damage an item
is_broken = item.damage_item(amount=1)

# Repair an item
item.repair_item(amount=None)  # Full repair
item.repair_item(amount=10)    # Partial repair

# Check durability
current = item.current_durability
maximum = item.template.get_effective_durability()
condition_percent = item.condition
```

## Crafting System

### Requirements
Items can specify crafting requirements:

```json
{
  "crafting_skill": "smithing",
  "crafting_difficulty": 25,
  "components_required": [
    {"type": "metal.mithril_ingot", "quantity": 4},
    {"type": "wood.ironwood", "quantity": 1},
    {"type": "fabric.leather", "quantity": 1}
  ]
}
```

### Quality Modifier
Items crafted by players have a quality modifier (0.5 - 1.5) based on:
- Crafter's skill level
- Component quality
- Tool quality bonuses
- Critical success chance

### Deconstruction
Items can be disassembled to recover materials:

```python
# Check if can disassemble
can_disassemble, message = item.can_disassemble(character)

# Get yield
yield_items = item.get_disassembly_yield(character_skill_level)

# Yield includes:
# - Base components (skill-modified)
# - Socketed gems (if any)
# - Quality affects yield percentage
```

## Item Instance vs Template

### ItemTemplate
- Defines base properties
- Shared across all instances
- Defines crafting recipes
- Sets base stats and requirements

### Item
- Individual instance
- Has unique modifications
- Tracks condition and durability
- Contains socketed gems
- Has applied enchantments
- Custom names and properties

## Example: Creating a Complete Item

```python
from app.models.item import ItemTemplate, Item
from app.models.item_constants import ItemType, WeaponType, MaterialType

# Create a template
template = ItemTemplate(
    template_id="mithril_longsword",
    name="Mithril Longsword",
    item_type=ItemType.WEAPON,
    base_type="weapon.blade.sword",
    weight=3.0,
    value=2500,
    quality_tier="rare",
    material=MaterialType.MITHRIL.value,
    socket_count=2,
    socket_types=["gem", "gem"],
    weapon_type=WeaponType.LONG_SWORD,
    base_damage_min=15,
    base_damage_max=25,
    attack_speed=1.0,
    max_durability=180,
    max_enchantments=2,
    enchantable=True
)

# Create an instance
item = Item(
    template=template,
    name=template.name,
    condition=100,
    quality_modifier=1.2  # High quality craft
)

# Initialize sockets
item.initialize_sockets()

# Socket a ruby
ruby = Item.query.filter_by(template_id="flawless_ruby").first()
item.socket_gem(0, ruby)

# Apply an enchantment
EnchantingSystem.enchant_item(item, 'sharpness', 'MasterSmith')

# Get final stats
stats = item.get_effective_stats()
```

## Integration with Game Systems

The item system integrates with:
- **Combat System**: Damage types, weapon speeds, armor class
- **Skill System**: Crafting requirements, enchanting levels
- **Economy System**: Item values, trading
- **Quest System**: Quest items, unique flags
- **Inventory System**: Weight, containers, equipment slots

