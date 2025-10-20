# Mudra

A web-based Multi-User Dungeon (MUD) built with Flask and vanilla JavaScript, featuring a classless/levelless 
progression system based on attributes, skills, and detailed item crafting/disassembly mechanics.

## Features

### Core Systems
- **Classless Progression**: No traditional classes - build your character through attributes and skills
- **Deep Item System**: Complex inheritance model with components, crafting, and disassembly
- **Real-time Communication**: WebSocket-based chat and game events
- **Command Parser**: Comprehensive command system for all game interactions
- **3D World System**: Full cartesian coordinate system with vertical movement (up/down)
- **Map Builder**: Visual tool for creating and managing game world
- **NPC Builder**: Comprehensive tool for creating NPCs with full character capabilities
- **Live Minimap**: Canvas-based real-time map display showing nearby rooms, connections, and player position

### Character System
- **21 Playable Races**: Each with unique ability modifiers, skills, and special abilities
- **Racial Traits**: Ability bonuses, skill affinities, special abilities, and resistances
- **Race-Specific Equipment Slots**: Some races have unique slots (tails) or restrictions (Centaurs can't wear leg armor)
- **4 Prime Attributes**: BODY, MIND, SPIRIT, KISMET
- **14 Sub-Attributes**: Detailed progression system with unlock requirements
- **Trial Points**: Used for HP, mana, movement, and attribute increases
- **Progress Points**: Used for learning and improving skills and spells
- **No Level System**: Power based entirely on race + attributes + skills + gear
- **Avatar Selection**: Choose from 500 unique character avatars during character creation
- **Account Points System**: Earn points based on achievements (triangular progression - tier number = points)
- **Character Slot Limits**: Non-admin accounts start with 3 character slots, purchasable up to 20
- **Shop System**: Spend account points to purchase additional character slots

### Item System
- **Comprehensive Item Types**: 101+ item types including weapons, armor, gems, tools, crafting materials, and more
- **Socket System**: Items can have gem/rune sockets for customization and power
- **Enchanting System**: Apply magical enchantments with various effects (damage types, resistances, stat bonuses)
- **Material System**: Items crafted from different materials (mithril, dragonhide, etc.) with unique properties
- **Damage Types**: 18 distinct damage types (physical, elemental, magical) with weapon and spell support
- **Weapon Properties**: Attack speeds, damage ranges, and weapon-specific damage types
- **Quality Tiers**: 10 quality levels from Junk to Mythic affecting item power
- **Durability System**: Items degrade with use and can be repaired
- **Weight & Encumbrance**: Realistic weight system with container weight reduction
- **Crafting System**: Create items from raw materials with skill requirements and quality modifiers
- **Disassembly**: Break down items to recover components (including socketed gems)
- **Item Flags**: Over 50 flags for special properties (magical, cursed, unique, quest items, etc.)
- **Equipment Slots**: 21 different equipment slots for complete character customization

### Skills & Spells
- **5 Skill Categories**: Combat, Crafting, Utility, Magic, Social
- **3 Spell Schools**: Mystical (divine), Magical (arcane), Psionics (mind)
- **Learning System**: Find teachers, meet requirements, spend progress points
- **Skill Synergies**: Related skills provide bonuses to each other

### World & Map System
- **3D Cartesian Coordinates**: Rooms positioned on X, Y, Z axes for clean spatial organization
- **6-Directional Movement**: North, South, East, West, Up, Down
- **Multiple Areas**: Starting Village, Whispering Woods, Iron Peaks, Shadowed Grove, Crystal Caverns
- **33+ Unique Rooms**: Each with detailed descriptions, items, NPCs, and environmental effects
- **Coordinate Validation**: Automatic checking to prevent room overlaps
- **Visual Map Builder**: Web-based tool for creating and editing rooms with real-time visualization

#### Door, Lock & Key System
- **Comprehensive Door Management**: Full-featured door system with locks and keys
- **Lock Difficulty Range (0-255)**:
  - **0**: No lock (door can be opened freely)
  - **1-100**: Normal locks (pickable by thieves with lockpicking skill)
  - **101-255**: Magical locks (enhanced by wizard lock spell)
- **10 Available Keys**: From common rusty iron keys to legendary artifact keys
- **Key Requirement**: Locked doors MUST have a key assigned (enforced by validation)
- **9 Door Flags** for advanced behavior:
  - **closed**: Door starts in closed state
  - **locked**: Door is locked (requires key or lockpicking)
  - **pick_proof**: Cannot be picked by thieves (immune to lockpicking)
  - **pass_proof**: Cannot pass through at all (impassable barrier)
  - **secret**: Hidden door (requires search or detection to find)
  - **hidden**: Not visible in room description
  - **no_lock**: Door cannot be locked
  - **no_knock**: Knock spell won't work on this door
  - **no_close**: Door cannot be closed
- **Spell Support**: Designed for knock spell (magical door opening) and wizard lock (increase difficulty)
- **Dual Validation**: Both frontend and backend enforce all rules consistently

## Technology Stack

### Backend
- **Flask**: Web framework with SocketIO for real-time communication
- **SQLAlchemy**: ORM for database operations
- **Redis**: Session caching and real-time data
- **PostgreSQL/SQLite**: Database for persistent data

### Frontend
- **HTML/CSS/JavaScript**: Vanilla frontend with modern UI
- **Socket.IO**: Real-time communication
- **Canvas**: Minimap rendering
- **Bootstrap**: Responsive UI framework

## Installation

### Prerequisites
- Python 3.8+
- Redis server
- PostgreSQL (optional, SQLite works for development)

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd Mudra
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. Load initial game data:
```bash
python scripts/load_data.py
```

7. Run the application:
```bash
python app.py
```

The game will be available at `http://localhost:5000`

## Game Data Structure

### JSON Data Files
- `data/world/areas.json` - Game areas and zones with level ranges
- `data/world/rooms.json` - Individual room data with 3D coordinates (33+ rooms)
- `data/items/templates.json` - Item templates and recipes
- `data/skills/skills.json` - Skill definitions and requirements
- `data/spells/spells.json` - Spell definitions and effects

### Room Coordinate System
Each room has:
- `x_coord`, `y_coord`, `z_coord` - 3D position in game world
- `exits` - Dictionary of directional exits (north, south, east, west, up, down)
- `area_id` - Reference to parent area
- Environmental properties (lighting, temperature, weather)
- Room flags (is_safe, is_indoors, is_water, is_air)

### Database Models
- **Player**: User accounts and authentication with account points tracking and character slot limits
- **Character**: Character data, attributes, and progression
- **Item**: Item instances and templates
- **Room**: Game world locations
- **Skill/Spell**: Character abilities and progression
- **ChatMessage**: Player chat communications with timestamps

## Game Commands

### Movement
- `north/n`, `south/s`, `east/e`, `west/w`, `up/u`, `down/d`
- `go <direction>` - Move in a specific direction

### Interaction
- `look/l` - Look at current room or object
- `examine/ex <object>` - Examine an object in detail
- `get/take <item>` - Pick up an item
- `drop <item>` - Drop an item
- `inventory/i` - View your inventory

### Equipment & Items
- `equip <item>` - Equip an item
- `unequip <item>` - Unequip an item
- `socket <item> <gem>` - Socket a gem into an item (planned)
- `unsocket <item> <socket_num>` - Remove a gem from a socket (planned)
- `enchant <item> <enchantment>` - Apply an enchantment to an item (planned)
- `repair <item>` - Repair a damaged item (planned)
- `craft <recipe>` - Craft an item from components (planned)
- `disassemble <item>` - Break down an item for components (planned)

### Social
- `say <message>` - Say something to the room
- `emote <action>` - Perform an emote
- `chat <message>` - Send a chat message to all players (use in main command input)
- `censor` - Toggle chat censorship on/off
- `who` - List online players

### System
- `help` - Show available commands
- `save` - Save your character
- `quit` - Exit the game

## Race System Deep Dive

### 21 Playable Races

The game features a comprehensive race system with 21 distinct races, each with unique traits:

**Common Races**
- **Human** - Versatile and adaptable, bonus trial point, faster skill learning
- **Dwarf** - Hardy crafters with smithing/mining bonuses, poison/magic resistance
- **Elf** - Graceful spellcasters with archery and magic bonuses
- **Halfling** - Lucky rogues with stealth bonuses and brave trait
- **Gnome** - Clever tinkerers with illusion magic and 15% magic resistance

**Mixed Heritage**
- **Half-Elf** - Diplomatic and versatile, combines human and elven traits
- **Half-Orc** - Strong warriors with relentless endurance

**Uncommon Races**
- **Tiefling** - Infernal magic users, 20% fire resistance, tail equipment slot
- **Goblin** - Cunning trappers with stealth and pack tactics
- **Orc** - Savage warriors with aggressive combat bonuses
- **Hobgoblin** - Disciplined soldiers with tactical genius
- **Lizardfolk** - Reptilian hunters with natural armor and tail slot
- **Kobold** - Dragon-blooded pack fighters with trap expertise
- **Aasimar** - Celestial healers with divine magic and radiant resistance

**Exotic Races**
- **Centaur** - Swift cavalry (40 ft speed), cannot wear leg/feet armor
- **Aarakocra** - Bird-like with flight (50 ft), keen sight bonuses
- **Minotaur** - Bull-like with perfect maze navigation and charge attacks
- **Tabaxi** - Cat-like explorers with feline agility and tail slot

**Fey Races**
- **Tortle** - Turtle-like with +4 natural armor, shell defense
- **Sprite** - Tiny fey with flight and at-will invisibility
- **Nymph** - Nature spirits with powerful charm abilities

### Racial Features

**Ability Modifiers**
- Applied automatically during character creation
- Add to player-allocated trial points
- Range from -5 to +5 per attribute
- Cover all 14 sub-attributes

**Racial Skills**
- Each race starts with 2-4 racial skills at level 1
- Example: Dwarves start with smithing, mining, stoneworking, appraise

**Skill Bonuses**
- Permanent bonuses to specific skills
- Major affinity: +10-15 bonus
- Minor affinity: +5-8 bonus
- Effective skill = base level + racial bonus

**Special Abilities**
- 2-5 unique abilities per race
- Combat abilities (charge, pack tactics, savage attacks)
- Vision abilities (darkvision, low-light vision, keen sight)
- Magical abilities (innate spells, resistances)
- Utility abilities (stonecunning, labyrinthine recall)

**Equipment Slot Variations**
- Standard races: 18 equipment slots
- Races with tails (Tiefling, Tabaxi, etc.): +1 tail slot
- Centaurs: Cannot wear leg/feet armor (equine body)
- Tortle: Cannot wear chest armor (natural shell)
- Sprite: Limited slots due to tiny size

**Resistances**
- Elemental resistances (fire, cold, poison, etc.)
- Magical resistances (charm, sleep, magic)
- Effect resistances (fear, radiant, necrotic)
- Values are percentages (10% = 10% damage reduction)

### Race Documentation

See `data/races/README.md` and `documentation/race_system.md` for complete information including:
- All 21 race definitions with full stats
- Ability modifier tables
- Skill bonus lists
- Special ability descriptions
- Equipment slot configurations
- API usage and integration examples

## Item System Deep Dive

### Item Type Categories

The game features 101+ distinct item types organized into categories:

**Weapons & Combat**
- Weapons (swords, axes, daggers, bows, etc.)
- Armor (chest, legs, head, hands, feet, etc.)
- Shields
- Ammunition (arrows, bolts)

**Magical Items**
- Scrolls (one-time spell casts)
- Wands and Staffs (multi-charge spells)
- Potions and Pills (consumable effects)

**Gems & Sockets**
- 12 gem types (ruby, sapphire, diamond, etc.)
- Each gem provides different bonuses
- Socketable gems add damage types or resistances
- Runes provide special effects

**Crafting & Materials**
- Raw materials (ores, wood, leather)
- Refined components (ingots, planks, strips)
- Essences and reagents
- Crafting tools (hammers, saws, looms)

**Containers & Storage**
- Backpacks and bags
- Sheaths and quivers
- Containers with weight reduction

**Utility Items**
- Keys and locks
- Maps and navigation tools
- Musical instruments
- Food and drink

### Damage Type System

18 damage types affect combat and spell interactions:

**Physical**: Slashing, Piercing, Bludgeoning, Physical  
**Elemental**: Fire, Cold, Lightning, Water, Air, Earth, Acid  
**Magical**: Light, Negative, Holy, Energy, Psychic, Sonic, Poison

Each weapon type has a primary damage type (daggers = piercing, swords = slashing), and enchantments/gems can add secondary damage types.

### Socket & Enchanting System

**Sockets**
- Items can have 0-3 sockets
- Socket types: Gem, Rune, Enchant
- Gems add stats, damage types, and resistances
- Quality affects gem bonuses

**Enchantments**
- Weapon enchantments: Flaming, Frost, Vampiric, Vorpal, etc.
- Armor enchantments: Protection, Fire Resistance, Fortitude, etc.
- Limited enchantment slots per item
- Requires enchanting skill and materials

### Material Properties

Items crafted from different materials have unique characteristics:

**Metals**: Iron, Steel, Mithril, Adamantine, Darksteel
- Affect weight and durability
- Mithril = lightweight, high durability
- Adamantine = extremely durable

**Woods**: Oak, Pine, Ironwood, Yew, Ebony
- Used in weapon handles, bows, shields
- Ironwood provides enhanced durability

**Fabrics**: Leather, Silk, Dragonhide, Scales
- For light armor and clothing
- Dragonhide = exceptional resistance

### Quality Tiers

Items range from Junk to Mythic quality:

1. Junk (worthless)
2. Poor (-20% stats)
3. Common (baseline)
4. Good (+10%)
5. Uncommon (+20%)
6. Rare (+40%)
7. Epic (+60%)
8. Legendary (+100%)
9. Artifact (+150%)
10. Mythic (+200%)

Quality affects damage, armor, durability, and value.

### Equipment Slots

21 equipment slots for complete customization:

- Head, Chest, Arms, Hands, Legs, Feet
- Neck, Shoulders, Waist
- Fingers (2), Wrists (2), Ears (2)
- Wielded weapons (main hand, off-hand)
- Held items, Shields
- Sheath, Quiver
- Floating items (magical)

### Crafting System

**Requirements**
- Specific skill and level
- Required components
- Crafting tools

**Quality Factors**
- Crafter skill level
- Component quality
- Tool bonuses
- Critical success chance

**Output**
- Quality modifier: 0.5 - 1.5
- Crafter signature on item
- Socket count (sometimes bonus sockets)
- Enchantability

### Item Documentation

See `documentation/item_system.md` for complete technical documentation including:
- All item types and their uses
- Complete gem bonus tables
- Enchantment definitions and requirements
- Material property charts
- Damage type interactions
- Code examples and API usage

## Development

### Project Structure
```
Mudra/
├── app/                    # Flask application
│   ├── routes/            # URL routes
│   ├── socket_handlers/   # WebSocket event handlers
│   ├── models/            # Database models
│   ├── systems/           # Game systems (combat, crafting, etc.)
│   └── utils/             # Utility functions
├── data/                  # JSON game data
│   ├── world/            # Areas and rooms
│   ├── items/            # Item templates and recipes
│   ├── skills/           # Skill definitions
│   └── spells/           # Spell definitions
├── static/               # Static files (CSS, JS, assets)
├── templates/            # HTML templates
└── tests/               # Test files
```

### Adding New Features
1. **Items**: Add templates to `data/items/templates.json`
2. **Skills**: Add definitions to `data/skills/skills.json`
3. **Spells**: Add definitions to `data/spells/spells.json`
4. **Rooms**: Use the Map Builder tool or manually edit `data/world/rooms.json`
5. **Commands**: Add handlers to `app/systems/commands.py`

### Map Builder Tool
The Map Builder is a visual web interface for creating and managing the game world:

```bash
# Run the map builder (separate from main app)
python map_builder.py
```

Access at `http://localhost:5001`

Features:
- Visual room placement with coordinate display
- Z-level filtering for multi-floor maps
- Automatic coordinate conflict detection
- Support for all 6 exit directions (N, S, E, W, Up, Down)
- Real-time map visualization with connection lines
- Room editing and deletion
- Drag-and-drop room repositioning (Ctrl+drag)
- Multi-select with drag selection (Shift+drag)
- Individual room selection controls:
  - **Click**: Select single room (clears other selections)
  - **Ctrl+Click**: Toggle room in/out of selection group
  - **Shift+Click**: Add room to selection group
- Automatic reciprocal exit creation
- Room ID recycling (reuses deleted IDs)
- Map export to JSON format
- Real-time coordinate display
- **Comprehensive Door/Lock/Key System** for room connections

#### Using the Door Editor in Map Builder

The Map Builder includes a full-featured door editor accessible when editing any room:

**Accessing the Door Editor:**
1. Select a room by clicking on it
2. Click any directional door button (North, South, East, West, Up, Down)
3. The door editor modal will open

**Door Properties:**
- **Door ID**: Unique identifier (required) - e.g., "village_gate_001"
- **Door Name**: Display name (required) - e.g., "Heavy Oak Gate"
- **Description**: Detailed description visible when examining the door
- **Key Template**: Select from 10 available keys (REQUIRED if door is locked)
- **Lock Difficulty** (0-255 slider):
  - **0**: No lock - door can be freely opened
  - **1-100**: Normal locks - pickable by thieves with lockpicking skill
    - 1-25: Very easy
    - 26-50: Easy
    - 51-75: Medium
    - 76-100: Hard
  - **101-255**: Magical locks - enhanced by wizard lock spell
    - 101-150: Magical
    - 151-200: Very magical
    - 201-255: Nearly impossible

**Door Flags (checkboxes):**
- **closed**: Door starts in closed state (players must open it)
- **locked**: Door is locked - requires key or lockpicking (MUST assign a key!)
- **pick_proof**: Cannot be picked by thieves (immune to lockpicking)
- **pass_proof**: Completely impassable barrier (even when open)
- **secret**: Hidden door requiring search or detection to find
- **hidden**: Not visible in room description (secret passive)
- **no_lock**: Door cannot be locked by any means
- **no_knock**: Knock spell won't work on this door
- **no_close**: Door cannot be closed

**Validation Rules (Enforced):**
- ✓ Locked doors MUST have a key assigned
- ✓ Cannot combine "No Lock" with "Locked"
- ✓ Cannot combine "No Close" with "Closed"
- ✓ Lock difficulty must be 0-255
- ✓ Door ID and name are required

**Available Keys:**
The system includes 10 pre-configured keys in `data/items/keys.json`:
- **key_001**: Rusty Iron Key (common, 5 gold)
- **key_002**: Brass Door Key (common, 15 gold)
- **key_003**: Steel Gate Key (uncommon, 50 gold)
- **key_004**: Silver Mansion Key (rare, 100 gold)
- **key_005**: Golden Treasury Key (epic, 500 gold)
- **key_006**: Skeleton Key (rare, 250 gold) - master key
- **key_007**: Mithril Dungeon Key (epic, 750 gold) - magical
- **key_008**: Obsidian Prison Key (legendary, 1000 gold) - cursed
- **key_009**: Crystal Tower Key (legendary, 1500 gold)
- **key_010**: Ancient Rune Key (artifact, 2500 gold) - quest item

**Usage Examples:**

*Simple Closed Door:*
- Door ID: "inn_room_001"
- Name: "Wooden Door"
- Flags: closed
- Lock Difficulty: 0
- Key: None

*Locked Door:*
- Door ID: "treasure_vault_001"
- Name: "Iron Treasury Door"
- Flags: closed, locked
- Lock Difficulty: 75
- Key: key_005 (Golden Treasury Key)

*Secret Magical Door:*
- Door ID: "wizard_tower_secret"
- Name: "Hidden Magical Portal"
- Flags: secret, hidden, locked, no_knock
- Lock Difficulty: 200
- Key: key_010 (Ancient Rune Key)

*Impassable Magical Barrier:*
- Door ID: "demon_seal_001"
- Name: "Demonic Seal"
- Flags: closed, locked, pass_proof, no_knock, pick_proof
- Lock Difficulty: 255
- Key: key_010 (Ancient Rune Key)

#### Door/Lock/Key System
The Map Builder includes a comprehensive door system for creating locked doors, secret passages, and complex access control:

**Lock Difficulty Ranges:**
- `0`: No lock
- `1-25`: Trivial locks (beginner thieves can pick)
- `26-50`: Easy locks (novice thieves can pick)
- `51-75`: Medium locks (experienced thieves needed)
- `76-100`: Hard locks (master thieves only)
- `101-150`: Magical locks (wizard lock spell)
- `151-200`: Very magical locks (powerful wizard lock)
- `201-255`: Nearly impossible (arcane sealing magic)

**Door Flags:**
- `closed`: Door starts in a closed state
- `locked`: Door is locked (requires matching key)
- `pick_proof`: Cannot be picked by thieves (must use key)
- `pass_proof`: Cannot pass through at all (impassable wall)
- `secret`: Hidden door that requires search to find
- `hidden`: Door is not visible in room descriptions
- `no_lock`: Door cannot be locked
- `no_knock`: Knock spell will not work on this door
- `no_close`: Door cannot be closed

**Key System:**
- Keys are item templates stored in `data/items/keys.json`
- 10 pre-configured key templates from rusty iron keys to ancient rune keys
- Each locked door MUST have an associated key template ID
- System prevents creating locked doors without assigned keys
- Keys can be unique (quest items) or common (dungeon keys)

**Using the Door Editor:**
1. Open a room for editing in the Map Builder
2. Click on any of the 6 door buttons (North, South, East, West, Up, Down)
3. Configure door properties:
   - Unique door ID
   - Door name and description
   - Key template (required if locked)
   - Lock difficulty (0-255 slider)
   - Door flags (checkboxes)
4. System validates:
   - Locked doors have keys assigned
   - Conflicting flags (e.g., no_lock + locked)
   - Required fields (door ID, name)

**Integration with Game Mechanics:**
- Players will need keys in inventory to unlock doors
- Thieves can attempt to pick locks (difficulty check)
- Wizards can cast "Knock" spell to open doors (unless no_knock flag)
- "Wizard Lock" spell increases lock difficulty by 100+
- Secret doors require search skill checks to discover

### NPC Builder Tool
The NPC Builder is a comprehensive visual interface for creating and managing NPCs:

```bash
# Run the NPC builder (separate from main app)
python npc_builder.py
```

Access at `http://localhost:5002`

Features:
- Full NPC creation with all character-like attributes
- Auto-generated unique NPC IDs (editable with duplicate prevention)
- Visual NPC list with search/filter functionality
- Complete attribute system (Body, Mind, Spirit, Kismet)
- Skills and spells management
- Currency management (gold, silver, copper)
- Room assignment with area-based filtering
- AI behavior configuration
- Faction and reputation settings
- Respawn time configuration
- Hostility and unique NPC flags

**NPC Capabilities:**
NPCs are functionally identical to player characters with additional AI features:
- Full attribute system (14 sub-attributes across 4 prime attributes)
- Skills and spells (can learn/cast like players)
- Inventory and equipment (can carry items, wear armor/weapons)
- Currency (can hold gold, silver, copper)
- HP, Mana, and Movement stats
- Trial Points and Progress Points
- Race selection with all racial bonuses

**NPC-Specific Features:**
- **AI Behavior**: Passive, Aggressive, Defensive, Merchant, Quest Giver, Guard, Patrol
- **Hostility**: Flag NPCs as hostile or friendly
- **Respawn Time**: Configure respawn delay in seconds (0 = no respawn)
- **Unique Flag**: Prevent respawn for special/quest NPCs
- **Faction**: Assign NPCs to factions for reputation system
- **Reputation Required**: Set minimum reputation to interact
- **Loot Tables**: Define items dropped on death (coming soon)
- **Dialogue Trees**: Create conversation paths (coming soon)

**Using the NPC Builder:**
1. Click "Create New NPC" to start building
2. Fill in basic information:
   - NPC ID (unique identifier)
   - Name (must be unique)
   - Race selection
   - Description
   - Avatar
3. Set location (room and coordinates)
4. Configure attributes manually or auto-calculate
5. Add skills and spells as needed
6. Set currency amounts
7. Configure AI behavior and properties
8. Save to database

**Editing Existing NPCs:**
- Click any NPC from the list to edit
- All fields are editable
- Changes save immediately to database
- Delete NPCs with confirmation prompt

**Integration with Game World:**
- NPCs appear in assigned rooms
- Can be interacted with by players
- Merchant NPCs can trade items
- Quest NPCs can give quests (when quest system is implemented)
- Hostile NPCs will attack players
- Respawn at configured intervals

### In-Game Minimap
The game features a live minimap displayed on the right panel:

Features:
- **Real-time Updates**: Automatically updates when you move
- **Periodic Refresh**: Updates every 5 seconds to show other players' movements
- **Nearby Rooms**: Shows rooms within 5 units in all directions
- **Connection Lines**: Visual display of room connections (North, South, East, West)
- **Up/Down Indicators**: Cyan arrows show vertical exits
- **Player Position**: Green dot indicates your current location
- **Styled Like Map Builder**: Consistent visual design with the map builder tool
- **Canvas-based Rendering**: Smooth, efficient rendering

The minimap provides spatial awareness and helps with navigation through complex areas. It stays synchronized with the game state through both immediate movement updates and periodic background refreshes.

### Coordinate System
The game uses a 3D cartesian coordinate system:
- **X-axis**: East (+) / West (-)
- **Y-axis**: North (+) / South (-)
- **Z-axis**: Up (+) / Down (-)

### Coordinate Validation
Validate room coordinates to prevent overlaps:

```bash
# Validate database coordinates
python scripts/validate_coordinates.py

# Validate a JSON file
python scripts/validate_coordinates.py --json data/world/rooms.json
```

The validator checks for:
- Coordinate overlaps between rooms
- Invalid exit directions
- Mismatched exit connections
- Coordinate range statistics

### Testing
```bash
# Run unit tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=app tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

### Phase 1: Core Infrastructure ✅
- [x] Flask app setup with SocketIO
- [x] Basic authentication system
- [x] Database models and migrations
- [x] Command parser framework
- [x] Simple room navigation

### Phase 2: Character System ✅
- [x] Attribute system implementation (14 sub-attributes)
- [x] Trial/progress point mechanics
- [x] Character creation UI
- [x] Attribute spending interface
- [x] Race system with 21 playable races
- [x] Racial ability modifiers and bonuses
- [x] Racial skills and skill bonuses
- [x] Race-specific equipment slots
- [x] Special racial abilities and resistances

### Phase 3: Item System ✅
- [x] Base item class hierarchy with 101+ item types
- [x] Item templates from JSON
- [x] Inventory management
- [x] Comprehensive equipment system with 21 slots
- [x] Socket system (gems and runes)
- [x] Enchanting system with damage types
- [x] Material system with weight/durability modifiers
- [x] Weapon damage types and attack speeds
- [x] Quality tier system (10 tiers)
- [x] Durability and repair mechanics
- [x] Weight and encumbrance system
- [x] Crafting system framework
- [x] Disassembly mechanics with component recovery
- [x] Item flags system (50+ flags)
- [ ] Full crafting UI integration
- [ ] Equipment display in character sheet
- [ ] Socket/enchant commands

### Phase 3.5: Chat System ✅
- [x] Chat command implementation
- [x] Chat message database storage
- [x] Real-time chat display
- [x] Chat history loading
- [x] Chat censorship system

### Phase 3.6: Account Points System ✅
- [x] Account points field added to Player model
- [x] Achievement-based point calculation (triangular progression - tier number = points)
- [x] Database migration for account_points field
- [x] Account screen UI updated with points display
- [x] Automatic point updates based on achievements

### Phase 3.7: Character Slot Limits & Shop System ✅
- [x] Character slot limits (3 for non-admin, 20 max)
- [x] Character slots field added to Player model
- [x] Database migration for character_slots field
- [x] Character creation enforces slot limits
- [x] Shop tab added to account screen
- [x] Character slot purchase system (10 points + 10 per slot)
- [x] Shop UI with purchase buttons and cost display

### Phase 4: Combat System (Planned)
- [ ] Combat engine
- [ ] Damage calculations
- [ ] Status effects
- [ ] Combat UI updates

### Phase 5: Skills & Spells (Planned)
- [ ] Skill system implementation
- [ ] Spell casting mechanics
- [ ] Learning/progression
- [ ] Skill UI

### Phase 6: World Building (In Progress)
- [x] 3D cartesian coordinate system
- [x] Area/room system with 33+ rooms
- [x] 5 distinct areas (Village, Forest, Mountains, Deep Forest, Crystal Caverns)
- [x] Visual Map Builder tool
- [x] Coordinate validation system
- [x] Multi-level support (up/down movement)
- [x] NPC framework with visual builder tool
- [ ] Loot generation
- [x] Minimap implementation

### Phase 7: Polish & Features (Planned)
- [ ] Advanced chat system
- [ ] Sound effects
- [ ] Advanced UI features
- [ ] Admin tools
- [ ] Testing and balancing

## Support

For questions, bug reports, or feature requests, please open an issue on GitHub.
