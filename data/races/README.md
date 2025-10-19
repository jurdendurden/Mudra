# Race System

This directory contains all race definitions for the game. Each race is defined in its own JSON file with complete information about ability modifiers, racial skills, equipment slots, and special abilities.

## Available Races

The game includes 21 distinct playable races:

### Common Races
- **Human** - Versatile and adaptable, bonus to luck and charisma
- **Dwarf** - Hardy and strong, excellent smiths and miners
- **Elf** - Graceful and magical, masters of archery and enchanting
- **Halfling** - Lucky and nimble, natural rogues
- **Gnome** - Clever tinkers with illusion magic

### Mixed Heritage
- **Half-Elf** - Combines human and elven traits
- **Half-Orc** - Strong warriors with savage fury

### Uncommon Races
- **Tiefling** - Infernal heritage, fire resistance
- **Goblin** - Small and cunning, trap experts
- **Orc** - Powerful warriors, aggressive nature
- **Hobgoblin** - Disciplined soldiers with tactical genius
- **Lizardfolk** - Reptilian with natural armor
- **Kobold** - Dragon-blooded, pack tactics
- **Aasimar** - Celestial heritage, divine magic

### Exotic Races
- **Centaur** - Half-horse, fast and strong
- **Aarakocra** - Bird-like with natural flight
- **Minotaur** - Bull-like, maze navigation
- **Tabaxi** - Cat-like, agile and curious
- **Tortle** - Turtle-like with shell armor

### Fey Races
- **Sprite** - Tiny fey with invisibility
- **Nymph** - Nature spirits with charm abilities

## Race File Structure

Each race JSON file contains:

### Basic Information
```json
{
  "name": "Race Name",
  "description": "Detailed description of the race",
  "size": "tiny|small|medium|large",
  "base_speed": 30
}
```

### Ability Modifiers
Modifiers applied to character attributes at creation:
```json
{
  "ability_modifiers": {
    "body": {
      "strength": 0,
      "durability": 0,
      "endurance": 0,
      "vitality": 0
    },
    "mind": {
      "intellect": 0,
      "cognition": 0,
      "willpower": 0,
      "psionics": 0
    },
    "spirit": {
      "mystical": 0,
      "magical": 0,
      "metaphysical": 0,
      "percipience": 0
    },
    "kismet": {
      "luck": 0,
      "charisma": 0
    }
  }
}
```

### Racial Skills
Skills that the race starts with or has affinity for:
```json
{
  "racial_skills": ["skill1", "skill2"],
  "skill_bonuses": {
    "skill_name": 10
  }
}
```

### Equipment Slots
Available equipment slots for the race:
```json
{
  "wearable_slots": [
    "head", "neck", "chest", "shoulders", "arms", "hands",
    "fingers", "waist", "legs", "feet", "wrist", "ears",
    "wield", "shield", "hold", "float", "tail", "sheath", "quiver"
  ]
}
```

Note: Some races have special slots (tail, etc.) while others cannot wear certain slots (Centaurs can't wear leg/feet armor).

### Special Abilities
Unique racial abilities:
```json
{
  "special_abilities": [
    {
      "name": "Ability Name",
      "description": "What the ability does"
    }
  ]
}
```

### Resistances
Damage or effect resistances (percentage-based):
```json
{
  "resistances": {
    "fire": 20,
    "poison": 15
  }
}
```

### Languages
Languages known by the race:
```json
{
  "languages": ["Common", "Racial Language"],
  "bonus_languages": ["Optional1", "Optional2"]
}
```

## Usage in Game

### Character Creation
When a character is created, racial bonuses are automatically applied:
1. Ability modifiers are added to base attributes
2. Racial skills are initialized at level 1
3. Racial skill bonuses are tracked separately
4. Equipment slots are determined by race

### During Gameplay
- `character.get_race_data()` - Get full race information
- `character.get_wearable_slots()` - Get available equipment slots
- `character.can_wear_slot(slot)` - Check if can wear in specific slot
- `character.get_racial_skill_bonuses()` - Get skill bonuses from race
- `character.get_effective_skill_level(skill)` - Get skill level + racial bonus
- `character.get_special_abilities()` - Get racial special abilities
- `character.get_resistances()` - Get racial resistances

## Adding New Races

To add a new race:

1. Create a new JSON file in this directory: `race_name.json`
2. Follow the structure shown above
3. Add the race to the character creation dropdown in `templates/game/create_character.html`
4. The race will be automatically loaded on next server start

### Balance Guidelines

**Ability Modifiers:**
- Total positive modifiers should roughly equal negative modifiers
- Strong races (Orc, Minotaur): +8 to +15 in physical, -5 to -10 in mental/spirit
- Magical races (Elf, Gnome): +5 to +10 in mental/spirit, -2 to -4 in physical
- Balanced races (Human, Half-Elf): Small bonuses, few penalties

**Skill Bonuses:**
- Major racial affinity: 10-15 bonus
- Minor affinity: 5-8 bonus
- Special racial skills: 3-5 bonus

**Special Abilities:**
- Each race should have 2-5 special abilities
- Abilities should be thematic and useful
- Some abilities can have trade-offs (Sprite: powerful but tiny)

**Resistances:**
- Elemental resistance: 10-20%
- Effect resistance (charm, fear): 5-15%
- Multiple resistances should be balanced with other weaknesses

## Integration

The race system integrates with:
- **Character Creation** - Automatic application of racial bonuses
- **Equipment System** - Slot restrictions based on race
- **Skill System** - Racial skill bonuses and affinities
- **Combat System** - Resistances and special abilities
- **Character Display** - Shows racial traits and abilities

## Files

- `human.json` - Versatile baseline race
- `dwarf.json` - Hardy crafters
- `elf.json` - Magical archers
- `halfling.json` - Lucky rogues
- `gnome.json` - Clever tinkerers
- `half_elf.json` - Diplomatic versatile
- `half_orc.json` - Strong warriors
- `tiefling.json` - Infernal magic
- `goblin.json` - Cunning trappers
- `orc.json` - Savage warriors
- `hobgoblin.json` - Tactical soldiers
- `lizardfolk.json` - Reptilian hunters
- `kobold.json` - Dragon-blooded pack fighters
- `aasimar.json` - Celestial healers
- `centaur.json` - Swift cavalry
- `aarakocra.json` - Aerial scouts
- `minotaur.json` - Maze warriors
- `tabaxi.json` - Agile explorers
- `tortle.json` - Armored survivalists
- `sprite.json` - Invisible tricksters
- `nymph.json` - Nature enchantresses

## Technical Details

- Race data is loaded once at server startup and cached
- Located in `app/utils/race_loader.py`
- Methods available through Character model
- All previous functionality is preserved

