# Race System Implementation

## Overview

The race system provides comprehensive racial traits, bonuses, and restrictions for all 21 playable races in Mudra. Each race is defined in its own JSON file with complete information about ability modifiers, skills, equipment slots, and special abilities.

## Features Implemented

### ✅ Individual Race JSON Files
- 21 race files in `data/races/` directory
- Each race has complete data including:
  - Ability score modifiers (all 14 attributes)
  - Racial skills (starting skills)
  - Skill bonuses (percentage bonuses)
  - Wearable equipment slots
  - Special abilities
  - Damage/effect resistances
  - Languages
  - Size and movement speed

### ✅ Race Loader Utility (`app/utils/race_loader.py`)
- Singleton pattern for efficient race data loading
- Caches all race data on first load
- Provides helper functions:
  - `get_race_data(race_name)` - Get full race data
  - `get_racial_ability_modifiers(race_name)` - Get attribute modifiers
  - `apply_racial_bonuses(character, race_name)` - Apply bonuses to character
  - `get_racial_skills(race_name)` - Get starting skills
  - `get_racial_skill_bonuses(race_name)` - Get skill bonuses
  - `get_wearable_slots(race_name)` - Get available equipment slots
  - `can_wear_slot(race_name, slot)` - Check slot availability
  - `get_special_abilities(race_name)` - Get racial abilities
  - `get_resistances(race_name)` - Get damage resistances

### ✅ Character Model Integration (`app/models/character.py`)
Added methods to Character class:
- `get_race_data()` - Get character's race information
- `get_wearable_slots()` - Get available equipment slots
- `can_wear_slot(slot_name)` - Check if can wear in slot
- `get_racial_skill_bonuses()` - Get racial skill bonuses
- `get_effective_skill_level(skill)` - Base skill + racial bonus
- `get_special_abilities()` - Get racial special abilities
- `get_resistances()` - Get racial resistances

### ✅ Character Creation Integration (`app/routes/game.py`)
- Automatically applies racial bonuses during character creation
- Initializes racial skills at level 1
- Preserves all previous functionality
- Racial modifiers add to player-allocated points

## Race Categories

### Common Races (5)
- **Human** - Versatile, +1 luck/charisma, extra trial point
- **Dwarf** - +2 STR, +3 DUR, smithing/mining bonuses, poison/magic resistance
- **Elf** - +2 INT/COG/MYS/MAG, archery/perception bonuses, low-light vision
- **Halfling** - +3 luck, stealth bonuses, lucky trait
- **Gnome** - +3 INT, +2 COG/MAG, illusion magic, 15% magic resistance

### Mixed Heritage (2)
- **Half-Elf** - +3 CHA, balanced bonuses, diplomatic
- **Half-Orc** - +4 STR, +3 END, relentless endurance

### Uncommon Races (7)
- **Tiefling** - Fire magic, 20% fire resistance, tail slot
- **Goblin** - Stealth, traps, fury of the small
- **Orc** - +5 STR, aggressive, savage fury
- **Hobgoblin** - Tactical, martial training, saving face
- **Lizardfolk** - Natural armor +2 AC, swimming, tail slot
- **Kobold** - Pack tactics, trap expert, tail slot
- **Aasimar** - Divine magic, healing hands, radiant resistance

### Exotic Races (4)
- **Centaur** - 40 ft speed, charge attack, no leg/feet armor
- **Aarakocra** - Flight 50 ft, keen sight, perception bonuses
- **Minotaur** - Goring rush, labyrinthine recall, horns attack
- **Tabaxi** - Feline agility, climbing, tail slot

### Fey Races (3)
- **Tortle** - +4 natural armor, shell defense, no chest armor
- **Sprite** - Tiny size, flight, invisibility, limited slots
- **Nymph** - +5 CHA, nature magic, blinding beauty

## Attribute Modifiers

Each race has modifiers for all 14 attributes across 4 categories:

**Body** (Physical attributes)
- Strength, Durability, Endurance, Vitality

**Mind** (Mental attributes)
- Intellect, Cognition, Willpower, Psionics

**Spirit** (Magical attributes)
- Mystical, Magical, Metaphysical, Percipience

**Kismet** (Social attributes)
- Luck, Charisma

### Example: Dwarf Modifiers
```python
{
  "body": {"strength": 2, "durability": 3, "endurance": 2, "vitality": 1},
  "mind": {"intellect": 0, "cognition": 1, "willpower": 2, "psionics": -1},
  "spirit": {"mystical": -2, "magical": -2, "metaphysical": 0, "percipience": 1},
  "kismet": {"luck": 0, "charisma": -1}
}
```

## Racial Skills and Bonuses

### Starting Skills
Each race gets 2-4 racial skills initialized at level 1:
- **Dwarf**: smithing, mining, stoneworking, appraise
- **Elf**: archery, perception, nature_lore, enchanting
- **Halfling**: stealth, lockpicking, cooking

### Skill Bonuses
Racial bonuses add to base skill levels:
- **Major affinity**: +10-15 bonus
- **Minor affinity**: +5-8 bonus
- **Resistance skills**: +10-20 bonus

### Effective Skill Calculation
```python
effective_level = base_skill_level + racial_bonus
```

Example: A Dwarf with smithing level 5 gets +10 racial bonus = effective level 15

## Equipment Slot System

### Standard Slots (18)
All races except Sprite can use:
- head, neck, chest, shoulders, arms, hands
- fingers, waist, legs, feet, wrist, ears
- wield, shield, hold, float, sheath, quiver

### Special Slots
Some races have unique equipment slots:
- **tail** - Tiefling, Lizardfolk, Kobold, Tabaxi (5 races)

### Slot Restrictions
Some races cannot use certain slots:
- **Centaur** - No legs/feet armor (equine lower body)
- **Tortle** - No chest armor (natural shell)
- **Sprite** - Very limited slots (tiny size)

### Usage
```python
# Check if character can wear an item
if character.can_wear_slot('tail'):
    # Can equip tail items
    pass

# Get all available slots
slots = character.get_wearable_slots()
```

## Special Abilities

Each race has 2-5 unique special abilities:

### Vision Abilities
- **Darkvision** - See in darkness (Dwarf, Orc, Goblin, etc.)
- **Low-Light Vision** - See farther in dim light (Elf, Half-Elf)
- **Keen Sight** - Perception bonuses (Aarakocra)

### Combat Abilities
- **Relentless Endurance** - Drop to 1 HP instead of 0 (Half-Orc)
- **Savage Attacks** - Extra critical damage (Orc)
- **Pack Tactics** - Bonus with allies nearby (Kobold, Goblin)
- **Charge** - Extra damage when charging (Centaur, Minotaur)

### Magical Abilities
- **Infernal Legacy** - Innate fire magic (Tiefling)
- **Healing Hands** - Touch healing (Aasimar)
- **Invisibility** - Turn invisible at will (Sprite)
- **Fey Step** - Short teleport through nature (Nymph)

### Utility Abilities
- **Stonecunning** - Detect traps in stone (Dwarf)
- **Lucky** - Reroll failures (Halfling)
- **Labyrinthine Recall** - Perfect navigation (Minotaur)

## Resistances

Racial resistances are percentage-based:

### Elemental Resistances
- **Fire**: Tiefling (20%), Tortle, etc.
- **Cold**: Various races
- **Poison**: Dwarf (15%), Tortle, etc.

### Magical Resistances
- **Magic**: Dwarf (10%), Gnome (15%)
- **Charm**: Elf (10%), Sprite (20%), Nymph (15%)
- **Radiant/Necrotic**: Aasimar (15% each)

### Usage in Combat
```python
resistances = character.get_resistances()
fire_resistance = resistances.get('fire', 0)
damage_taken = base_damage * (1 - fire_resistance/100)
```

## Integration Points

### Character Creation
1. Player selects race and allocates 20 trial points
2. Racial ability modifiers are added to allocated points
3. Racial skills are initialized at level 1
4. Character's derived stats are calculated with bonuses

### Equipment System
- Check `character.can_wear_slot(slot)` before equipping
- Display available slots based on race
- Restrict equipping to valid slots

### Skill System
- Use `character.get_effective_skill_level(skill)` for checks
- Display both base and effective skill levels
- Apply racial bonuses to skill checks

### Combat System
- Apply racial resistances to incoming damage
- Use special abilities in combat calculations
- Consider natural weapons (claws, horns, bite, etc.)

## File Structure

```
data/races/
├── README.md                 # Race system documentation
├── human.json               # Baseline versatile race
├── dwarf.json               # Hardy crafters
├── elf.json                 # Magical archers
├── halfling.json            # Lucky rogues
├── gnome.json               # Clever tinkerers
├── half_elf.json            # Diplomatic hybrid
├── half_orc.json            # Strong warriors
├── tiefling.json            # Infernal magic
├── goblin.json              # Cunning trappers
├── orc.json                 # Savage warriors
├── hobgoblin.json           # Tactical soldiers
├── lizardfolk.json          # Reptilian hunters
├── kobold.json              # Dragon-blooded pack fighters
├── aasimar.json             # Celestial healers
├── centaur.json             # Swift cavalry
├── aarakocra.json           # Aerial scouts
├── minotaur.json            # Maze warriors
├── tabaxi.json              # Agile explorers
├── tortle.json              # Armored survivalists
├── sprite.json              # Invisible tricksters
└── nymph.json               # Nature enchantresses

app/utils/
└── race_loader.py           # Race loading and helper functions

app/models/
└── character.py             # Character model with race methods

app/routes/
└── game.py                  # Character creation with racial bonuses
```

## API Reference

### Race Loader Functions

```python
from app.utils.race_loader import *

# Get race data
race_data = get_race_data('Dwarf')

# Get all available races
all_races = get_all_races()

# Get ability modifiers
modifiers = get_racial_ability_modifiers('Elf')

# Apply bonuses to character
apply_racial_bonuses(character, 'Human')

# Get racial skills
skills = get_racial_skills('Dwarf')
bonuses = get_racial_skill_bonuses('Elf')

# Get equipment info
slots = get_wearable_slots('Centaur')
can_wear = can_wear_slot('Tiefling', 'tail')

# Get abilities and resistances
abilities = get_special_abilities('Kobold')
resistances = get_resistances('Aasimar')

# Get additional info
description = get_race_description('Human')
speed = get_base_speed('Centaur')  # Returns 40
size = get_size('Sprite')  # Returns "tiny"
langs, bonus_langs = get_languages('Elf')
```

### Character Model Methods

```python
# Access through character instance
race_info = character.get_race_data()
slots = character.get_wearable_slots()
can_wear = character.can_wear_slot('tail')

skill_bonuses = character.get_racial_skill_bonuses()
effective_skill = character.get_effective_skill_level('smithing')

abilities = character.get_special_abilities()
resistances = character.get_resistances()
```

## Testing

All races load successfully:
```bash
python -c "from app.utils.race_loader import get_all_races; print(len(get_all_races()))"
# Output: 21
```

Test racial bonuses:
```bash
python -c "from app.utils.race_loader import get_racial_ability_modifiers; print(get_racial_ability_modifiers('Dwarf'))"
```

## Backward Compatibility

✅ All previous functionality is preserved:
- Existing characters work without modification
- Character creation flow unchanged (just adds bonuses)
- All existing database fields remain compatible
- No breaking changes to API or routes

## Future Enhancements

Potential additions to the race system:
- [ ] Racial feat trees
- [ ] Age categories with modifiers
- [ ] Racial reputation system
- [ ] Sub-races (Wood Elf, Mountain Dwarf, etc.)
- [ ] Racial transformation abilities
- [ ] Dynamic racial abilities that improve with level

