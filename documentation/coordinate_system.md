# Character Coordinate System

## Overview
The character coordinate system tracks player positions using X, Y, Z coordinates. This ensures characters are always placed in valid rooms and handles edge cases where a character's coordinates don't match any existing room.

## Implementation Details

### Database Fields
Each character has three coordinate fields:
- `x_coord`: X coordinate (east/west)
- `y_coord`: Y coordinate (north/south)
- `z_coord`: Z coordinate (up/down)
- `current_room_id`: Foreign key to the room they're in

### Starting Village
- The default starting location is the Village Square (room_001)
- New characters are automatically placed here upon creation
- Characters with invalid coordinates are moved here upon login

### Core Functions

#### `get_starting_village_location()`
Returns the starting village room and its coordinates.
- Queries for room_id 'room_001' (Village Square)
- Fallback: Returns (0, 0, 0) if room not found
- Returns: (room, x, y, z)

#### `validate_character_location(character)`
Validates and fixes character locations on login.
- Checks if character has null coordinates → moves to Starting Village
- Checks if room exists at character's coordinates → moves to Starting Village if invalid
- Updates current_room_id to match coordinates if needed
- Returns: True if character was reset, False if location was valid

### Character Creation
When a character is created:
1. Starting Village room is queried
2. Character coordinates are set to Starting Village location
3. `current_room_id` is set to the Starting Village room ID

### Login/Character Selection
When a character logs in:
1. `validate_character_location()` is called
2. Character location is validated against existing rooms
3. Invalid locations are automatically corrected
4. User is notified if they were moved to Starting Village

### Maintenance Script

#### `scripts/fix_character_coords.py`
Run this script to fix coordinates for all existing characters:
```bash
python scripts/fix_character_coords.py
```

Features:
- Validates all character coordinates
- Moves characters with invalid coordinates to Starting Village
- Updates room_id to match coordinates
- Provides detailed summary of changes

## Usage Examples

### Creating a New Character
```python
# In create_character route
starting_room, x, y, z = get_starting_village_location()
character.x_coord = x
character.y_coord = y
character.z_coord = z
if starting_room:
    character.current_room_id = starting_room.id
```

### Loading a Character
```python
# In play_character route
was_reset = validate_character_location(character)
if was_reset:
    flash('Your location was invalid and you have been moved to the Starting Village.', 'info')
```

### Moving a Character
When implementing movement commands, update all three values:
```python
character.x_coord = new_x
character.y_coord = new_y
character.z_coord = new_z
character.current_room_id = new_room.id
```

## Safety Features

1. **Null Check**: Characters with null coordinates are automatically fixed
2. **Room Validation**: Coordinates are validated against existing rooms
3. **Automatic Reset**: Invalid locations are automatically corrected to Starting Village
4. **User Notification**: Players are informed when their location is reset
5. **Fallback Behavior**: System has fallback coordinates (0, 0, 0) if Starting Village room not found

## Maintenance

### When Adding New Rooms
- No special action needed
- Coordinate validation happens automatically on character login

### When Removing Rooms
1. Run `fix_character_coords.py` to move affected characters
2. Or wait for characters to login (they'll be automatically moved if their room is invalid)

### Debugging
To check a character's location:
```python
print(f"Character: {character.name}")
print(f"Coordinates: ({character.x_coord}, {character.y_coord}, {character.z_coord})")
print(f"Room ID: {character.current_room_id}")

# Validate location
room = Room.query.filter_by(
    x_coord=character.x_coord,
    y_coord=character.y_coord,
    z_coord=character.z_coord
).first()
print(f"Room exists: {room is not None}")
```

## Recent Updates
- **2024-10-15**: Implemented coordinate tracking system
  - Added `get_starting_village_location()` helper
  - Added `validate_character_location()` validator
  - Updated character creation to set coordinates
  - Updated login to validate coordinates
  - Created maintenance script to fix existing characters
  - All 4 existing characters validated and fixed

