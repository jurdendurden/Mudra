# Door System Migration Guide

## Overview
A comprehensive door/lock/key system has been implemented for the Map Builder. This guide explains how to apply the database migration and start using the new features.

## Database Migration

The door system requires a new `doors` column in the `rooms` table. Run the migration:

```bash
# Apply the migration
flask db upgrade
```

Or if using Alembic directly:
```bash
alembic upgrade head
```

The migration file is: `migrations/versions/k7l8m9n0o1p2_add_doors_column_to_rooms_table.py`

## Files Modified

### Backend Models
- `app/models/room.py` - Added `doors` column and helper methods
- `app/models/item.py` - Added key item support methods
- `map_builder.py` - Added door management API endpoints

### Frontend
- `templates/map_builder/index.html` - Added door editor UI and JavaScript functions

### Data Files
- `data/items/keys.json` - New file with 10 pre-configured key templates

### Documentation
- `README.md` - Added comprehensive door system documentation

## Using the Door System

### 1. Start the Map Builder
```bash
python map_builder.py
```
Access at http://localhost:5001

### 2. Edit a Room
- Open an existing room for editing
- Scroll down to the "Doors" section
- Click on any direction (North, South, East, West, Up, Down)

### 3. Configure Door Properties
- **Door ID**: Unique identifier (auto-generated)
- **Door Name**: Display name (e.g., "Heavy Oak Door")
- **Description**: Detailed description for players
- **Key Template**: Select from available keys (required if locked)
- **Lock Difficulty**: 0-255 (0-100 normal, 101-255 magical)
- **Flags**: Check appropriate boxes for door behavior

### 4. Important Rules
- ✅ Locked doors MUST have a key assigned
- ✅ Cannot have both "no_lock" and "locked" flags
- ✅ Cannot have both "no_close" and "closed" flags
- ✅ Lock difficulty must be 0-255

## Lock Difficulty Guide

| Range | Description | Pickability |
|-------|-------------|-------------|
| 0 | No lock | N/A |
| 1-25 | Trivial | Beginner thieves |
| 26-50 | Easy | Novice thieves |
| 51-75 | Medium | Experienced thieves |
| 76-100 | Hard | Master thieves |
| 101-150 | Magical | Wizard lock spell |
| 151-200 | Very Magical | Powerful wizard lock |
| 201-255 | Nearly Impossible | Arcane sealing |

## Door Flags Explained

- **closed**: Door starts closed (can be opened)
- **locked**: Door is locked (needs key)
- **pick_proof**: Cannot be picked (key only)
- **pass_proof**: Impassable (like a wall)
- **secret**: Hidden (requires search)
- **hidden**: Not in room description
- **no_lock**: Cannot be locked
- **no_knock**: Knock spell won't work
- **no_close**: Cannot be closed

## Key Templates

10 pre-configured keys are available in `data/items/keys.json`:

1. **key_001** - Rusty Iron Key (common)
2. **key_002** - Brass Door Key (common)
3. **key_003** - Steel Gate Key (uncommon)
4. **key_004** - Silver Mansion Key (rare)
5. **key_005** - Golden Treasury Key (epic)
6. **key_006** - Skeleton Key (rare, master key)
7. **key_007** - Mithril Dungeon Key (epic, magical)
8. **key_008** - Obsidian Prison Key (legendary, cursed)
9. **key_009** - Crystal Tower Key (legendary, magical)
10. **key_010** - Ancient Rune Key (artifact, quest item)

## Game Integration (Future)

The door system is designed to integrate with:
- **Movement System**: Check door state before allowing passage
- **Lockpicking**: Thief skill checks against lock difficulty
- **Knock Spell**: Wizard spell to open doors
- **Wizard Lock Spell**: Increases lock difficulty by 100+
- **Search Skill**: Find secret/hidden doors
- **Key Inventory**: Check if player has matching key

## API Endpoints

New endpoints added to map_builder.py:

- `GET /api/rooms/<id>/doors` - Get all doors for a room
- `POST /api/rooms/<id>/doors/<direction>` - Create/update door
- `DELETE /api/rooms/<id>/doors/<direction>` - Delete door
- `GET /api/keys` - Get available key templates
- `POST /api/doors/validate` - Validate door data

## Troubleshooting

### Migration Fails
If the migration fails, check that you don't have any existing `doors` column:
```sql
-- Check if column exists
PRAGMA table_info(rooms);

-- If it exists, drop it first
ALTER TABLE rooms DROP COLUMN doors;
```

### Keys Not Loading
Ensure `data/items/keys.json` exists and is valid JSON:
```bash
python -m json.tool data/items/keys.json
```

### Door Buttons Not Showing
Clear browser cache and reload the Map Builder. Check browser console for errors.

## Next Steps

1. Run the migration: `flask db upgrade`
2. Restart the map builder: `python map_builder.py`
3. Open an existing room and try creating a door
4. Assign keys to locked doors
5. Test different flag combinations

## Support

If you encounter issues:
1. Check the browser console for JavaScript errors
2. Check the Flask logs for API errors
3. Verify the migration was applied: `flask db current`
4. Ensure all required files exist

