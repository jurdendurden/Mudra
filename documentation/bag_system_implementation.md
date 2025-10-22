# WoW-Style Bag System Implementation

## Overview
This document describes the implementation of the World of Warcraft-style bag system for the MUD game. Players can equip bags to increase their inventory capacity, with 5 quick bag slots for easy access.

## Features Implemented

### 1. Character Bag Slots
- **Location**: `app/models/character.py`
- Added `bag_slots` JSON field to Character model
- Format: `{0: item_id, 1: item_id, 2: item_id, 3: item_id, 4: item_id}`
- 5 quick bag slots (0-4) that can hold container items

### 2. Container Items with Slot Capacity
- **Location**: `data/items/containers.json`
- Added 12 new bag types with varying capacities:
  - Small Pouch: 4 slots
  - Leather Pouch: 6 slots
  - Canvas Bag: 8 slots
  - Leather Bag: 10 slots
  - Traveler's Pack: 12 slots
  - Adventurer's Backpack: 16 slots
  - Silk Bag: 18 slots
  - Reinforced Backpack: 20 slots
  - Enchanter's Satchel: 24 slots
  - Void-Touched Bag: 28 slots
  - Enchanter's Pack: 32 slots
  - Bottomless Bag: 40 slots

### 3. API Endpoints
- **Location**: `app/routes/api.py`

#### Get Inventory (Enhanced)
```
GET /api/character/<int:character_id>/inventory
```
Returns:
- `inventory`: Array of item objects
- `bag_slots`: Object mapping slot numbers (0-4) to bag data
- `total_slots`: Base slots (20) + equipped bag capacities
- `used_slots`: Number of items in inventory

#### Equip Bag to Slot
```
POST /api/character/<int:character_id>/bag-slot/<int:slot_num>
Body: {"item_id": <int>}
```
- Equips a container item to a quick bag slot (0-4)
- Validates that the item is a container
- Checks for existing bags in the slot
- Returns success message and slot info

#### Unequip Bag from Slot
```
DELETE /api/character/<int:character_id>/bag-slot/<int:slot_num>
```
- Removes a bag from the specified quick bag slot
- Returns success message

### 4. User Interface
- **Location**: `templates/game/index.html`

#### Visual Components
- **Bag Slots Container**: 5 horizontal slots displayed above inventory grid
- **Bag Slot Display**: 
  - Shows bag icon when equipped
  - Shows slot capacity number in gold text
  - Numbered 1-5 for easy reference
  - Empty slots show just the slot number
  - Hover effect with gold border
  - Green border when bag is equipped

#### Drag and Drop
- Container items in inventory are draggable
- Drag bags to quick slots to equip them
- Click equipped bag to unequip (with confirmation)
- Visual feedback during drag operations

#### Dynamic Inventory Grid
- Base inventory: 20 slots
- Grid expands based on equipped bags
- Shows "X/Y slots" where Y = 20 + bag capacities
- Grid uses 8 columns for clean layout

### 5. Styling
CSS classes added:
- `.bag-slots-container`: Container for the 5 quick bag slots
- `.bag-slots`: Flexbox layout for horizontal display
- `.bag-slot`: Individual slot styling with hover effects
- `.bag-slot.has-bag`: Style for equipped bags
- `.bag-slot-number`: Small number in corner (1-5)
- `.bag-slot-capacity`: Gold text showing bag capacity
- `.bag-slot-icon`: Container for bag icon image

## Database Schema

### Migration
- **File**: `migrations/versions/7feb7c1dcc0f_add_bag_slots_to_characters.py`
- Added `bag_slots` column to `characters` table
- Type: JSON (stores object mapping slot number to item ID)
- Default: NULL (initialized to empty dict when first used)

## Technical Implementation Details

### Inventory Calculation
```python
base_slots = 20
total_slots = base_slots

for slot_num in range(5):
    if bag_slots[slot_num]:
        bag = Item.query.get(bag_slots[slot_num])
        if bag and bag.template:
            total_slots += bag.template.container_capacity
```

### Drag and Drop Flow
1. User drags container item from inventory
2. `dragItem()` captures item ID in `draggedItemId` variable
3. User drops on a bag slot (0-4)
4. `dropBagToSlot()` validates item is a container
5. POST request to `/api/character/<id>/bag-slot/<slot>`
6. Server validates and updates `character.bag_slots`
7. Client refreshes inventory display
8. Total slots updated, grid expands if needed

### Unequip Flow
1. User clicks equipped bag slot
2. Confirmation dialog appears
3. On confirm, DELETE request to endpoint
4. Server removes bag from slot (sets to None)
5. Client refreshes inventory display
6. Total slots reduced, grid contracts

## Testing

All tests passed successfully:
- ✓ Character bag_slots field exists and works
- ✓ 16 bag templates loaded with proper capacities
- ✓ Bag items can be created for characters
- ✓ Bags can be equipped to quick slots
- ✓ Inventory slot calculation is accurate
- ✓ Bags can be unequipped from slots
- ✓ Database operations use flag_modified for JSON fields
- ✓ UI displays bag slots and handles drag-and-drop

## User Experience

### Equipping a Bag
1. Open inventory tab
2. Find a bag/pouch/container item
3. Drag the bag to one of the 5 quick bag slots at top
4. Bag icon appears in slot with capacity number
5. Inventory capacity increases automatically
6. More empty slots appear in grid

### Unequipping a Bag
1. Click on an equipped bag in quick slots
2. Confirm the unequip action
3. Bag returns to inventory
4. Inventory capacity decreases
5. Grid contracts to new total

### Visual Feedback
- Empty slots: Gray with just a number (1-5)
- Equipped bags: Shows icon + capacity in gold
- Hover: Gold border glow
- Drag over: Visual indication of drop target
- Success/Error: Messages in game output

## Future Enhancements

### Potential Features
1. **Specialized Bags**
   - Herb bags (only hold herbs)
   - Mining bags (only hold ore/gems)
   - Enchanting bags (only hold reagents)

2. **Bag Quality Tiers**
   - Common bags (4-8 slots)
   - Uncommon bags (10-16 slots)
   - Rare bags (18-24 slots)
   - Epic bags (28-32 slots)
   - Legendary bags (40 slots)

3. **Bag Container Access**
   - Click bag to view its contents
   - Separate UI for each bag's items
   - Move items between bags

4. **Bag Keyring**
   - Special slot for keyring container
   - Doesn't count toward bag slots
   - Auto-stores keys

5. **Weight Reduction**
   - Some bags reduce weight of contents
   - Engineering bags reduce engineering items
   - Mining bags reduce ore weight

## Files Modified

1. `app/models/character.py` - Added bag_slots field
2. `app/routes/api.py` - Added bag slot endpoints and updated inventory API
3. `templates/game/index.html` - Added UI components, styling, and JavaScript
4. `data/items/containers.json` - Added 12 new bag types
5. `migrations/versions/7feb7c1dcc0f_add_bag_slots_to_characters.py` - Database migration

## Dependencies

- Flask-SQLAlchemy: For JSON field support
- SQLAlchemy flag_modified: For JSON field change tracking
- HTML5 Drag and Drop API: For bag dragging
- Fetch API: For AJAX requests to endpoints

## Notes

- Bags themselves take up inventory slots when not equipped
- Equipped bags add their capacity to total inventory
- Maximum 5 bags can be equipped at once
- Base inventory is always 20 slots
- Maximum possible inventory: 20 + (5 × 40) = 220 slots

