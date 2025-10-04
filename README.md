# Mudra MUD

A web-based Multi-User Dungeon (MUD) built with Flask and vanilla JavaScript, featuring a classless progression system based on attributes, skills, and detailed item crafting/disassembly mechanics.

## Features

### Core Systems
- **Classless Progression**: No traditional classes - build your character through attributes and skills
- **Deep Item System**: Complex inheritance model with components, crafting, and disassembly
- **Real-time Communication**: WebSocket-based chat and game events
- **Command Parser**: Comprehensive command system for all game interactions
- **Minimap**: Canvas-based real-time map display

### Character System
- **4 Prime Attributes**: BODY, MIND, SPIRIT, KISMET
- **16 Sub-Attributes**: Detailed progression system with unlock requirements
- **Trial Points**: Used for HP, mana, movement, and attribute increases
- **Progress Points**: Used for learning and improving skills and spells
- **No Level System**: Power based entirely on attributes + skills + gear

### Item System
- **Deep Inheritance**: Complex item hierarchy with components and recipes
- **Crafting System**: Create items from raw materials with skill requirements
- **Disassembly**: Break down items to recover components
- **Quality System**: Items have quality tiers affecting their properties
- **Equipment Slots**: Weapons, armor, accessories, and tools

### Skills & Spells
- **5 Skill Categories**: Combat, Crafting, Utility, Magic, Social
- **3 Spell Schools**: Mystical (divine), Magical (arcane), Psionics (mind)
- **Learning System**: Find teachers, meet requirements, spend progress points
- **Skill Synergies**: Related skills provide bonuses to each other

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
- `data/world/areas.json` - Game areas and zones
- `data/world/rooms.json` - Individual room data
- `data/items/templates.json` - Item templates and recipes
- `data/skills/skills.json` - Skill definitions and requirements
- `data/spells/spells.json` - Spell definitions and effects

### Database Models
- **Player**: User accounts and authentication
- **Character**: Character data, attributes, and progression
- **Item**: Item instances and templates
- **Room**: Game world locations
- **Skill/Spell**: Character abilities and progression

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

### Equipment
- `equip <item>` - Equip an item
- `unequip <item>` - Unequip an item

### Social
- `say <message>` - Say something to the room
- `emote <action>` - Perform an emote
- `who` - List online players

### System
- `help` - Show available commands
- `save` - Save your character
- `quit` - Exit the game

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
4. **Rooms**: Add room data to `data/world/rooms.json`
5. **Commands**: Add handlers to `app/systems/commands.py`

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
- [x] Attribute system implementation
- [x] Trial/progress point mechanics
- [x] Character creation UI
- [x] Attribute spending interface

### Phase 3: Item System (In Progress)
- [x] Base item class hierarchy
- [x] Item templates from JSON
- [x] Inventory management
- [ ] Basic equipment system
- [ ] Crafting system
- [ ] Disassembly mechanics

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

### Phase 6: World Building (Planned)
- [ ] Area/room system
- [ ] NPC framework
- [ ] Loot generation
- [ ] Minimap implementation

### Phase 7: Polish & Features (Planned)
- [ ] Advanced chat system
- [ ] Sound effects (optional)
- [ ] Advanced UI features
- [ ] Admin tools
- [ ] Testing and balancing

## Support

For questions, bug reports, or feature requests, please open an issue on GitHub.
