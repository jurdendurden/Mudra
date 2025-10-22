// map_builder_room_editor.js
// Room/area modal logic, exit management, dropdown population
import { areas, rooms, selectedRoom, roomModal, setSelectedRoom, setRooms, CANVAS_CENTER, CANVAS_PADDING, GRID_SIZE, API_BASE, doorModal } from './map_builder_core.js';
import { createRoom, updateRoom, deleteRoom as APIDeleteRoom, createArea, fetchRooms } from './map_builder_api.js';
import { renderMap, renderAreaList, renderRoomList, updateSelectionDisplay } from './map_builder_render.js';
import { addToUndoHistory } from './map_builder_undo.js';
let currentDoorDirection = null;
// Populate area select dropdown in room modal
export function populateAreaSelect() {
    const select = document.getElementById('areaSelect');
    // Remove existing options
    select.innerHTML = '';
    // Add the default "Select Area" option programmatically
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Select Area';
    select.appendChild(defaultOption);
    areas.forEach(area => {
        const option = document.createElement('option');
        option.value = area.id;
        option.textContent = area.name;
        select.appendChild(option);
    });
}

// Open room editor modal
export function openRoomEditor(room) {
    setSelectedRoom(room);
    
    // Populate modal fields with room data
    document.getElementById('roomId').value = room.id || '';
    document.getElementById('roomName').value = room.name || '';
    document.getElementById('areaSelect').value = room.area_id || '';
    document.getElementById('roomX').value = room.x ?? 0;
    document.getElementById('roomY').value = room.y ?? 0;
    document.getElementById('roomZ').value = room.z ?? 0;
    document.getElementById('roomDescription').value = room.description || '';
    document.getElementById('roomLighting').value = room.lighting || 'normal';

    // Exits (checkboxes)
    document.getElementById('exitNorth').checked = room.exits?.north || false;
    document.getElementById('exitSouth').checked = room.exits?.south || false;
    document.getElementById('exitEast').checked = room.exits?.east || false;
    document.getElementById('exitWest').checked = room.exits?.west || false;
    document.getElementById('exitUp').checked = room.exits?.up || false;
    document.getElementById('exitDown').checked = room.exits?.down || false;

    
    roomModal.show();
}
export async function saveRoom() {
    const x = parseInt(document.getElementById('roomX').value);
    const y = parseInt(document.getElementById('roomY').value);
    const z = parseInt(document.getElementById('roomZ').value);
    const currentRoomId = document.getElementById('roomId').value;
    
    // Convert exit checkboxes to room_id references
    const directionOffsets = {
        'north': { x: 0, y: 1, z: 0 },
        'south': { x: 0, y: -1, z: 0 },
        'east': { x: 1, y: 0, z: 0 },
        'west': { x: -1, y: 0, z: 0 },
        'up': { x: 0, y: 0, z: 1 },
        'down': { x: 0, y: 0, z: -1 }
    };
    
    const oppositeDirections = {
        'north': 'south',
        'south': 'north',
        'east': 'west',
        'west': 'east',
        'up': 'down',
        'down': 'up'
    };
    
    const exits = {};
    const roomsToUpdate = []; // Track rooms that need reciprocal exit changes
    
    ['north', 'south', 'east', 'west', 'up', 'down'].forEach(direction => {
        const checkboxId = `exit${direction.charAt(0).toUpperCase() + direction.slice(1)}`;
        const isChecked = document.getElementById(checkboxId).checked;
        
        const offset = directionOffsets[direction];
        const targetX = x + offset.x;
        const targetY = y + offset.y;
        const targetZ = z + offset.z;
        
        const targetRoom = rooms.find(r => 
            r.x === targetX && r.y === targetY && (r.z || 0) === targetZ
        );
        
        if (targetRoom) {
            if (isChecked) {
                // Add exit
                exits[direction] = targetRoom.room_id;
                
                // Track this room for reciprocal exit addition
                roomsToUpdate.push({
                    room: targetRoom,
                    direction: oppositeDirections[direction],
                    targetRoomId: currentRoomId,
                    add: true
                });
            } else {
                // Exit unchecked - remove reciprocal exit if it exists
                if (targetRoom.exits && targetRoom.exits[oppositeDirections[direction]] === currentRoomId) {
                    roomsToUpdate.push({
                        room: targetRoom,
                        direction: oppositeDirections[direction],
                        targetRoomId: currentRoomId,
                        add: false
                    });
                }
            }
        }
    });
    
    const formData = {
        room_id: currentRoomId,
        name: document.getElementById('roomName').value,
        description: document.getElementById('roomDescription').value,
        area_id: document.getElementById('areaSelect').value || null,
        x: x,
        y: y,
        z: z,
        exits: exits,
        lighting: document.getElementById('roomLighting').value
    };
    
    try {
        let updatedRoom = null;
        let previousState = null;
        
        if (selectedRoom) {
            // Save previous state for undo
            previousState = JSON.parse(JSON.stringify(selectedRoom));
            
            updatedRoom = await updateRoom(selectedRoom.id, formData);
            
        } else {
            updatedRoom = await createRoom(formData);
        }
        
        if (updatedRoom) {

            // Add to undo history if this was an update
            if (previousState) {
                addToUndoHistory({
                    type: 'update',
                    room: updatedRoom,
                    previousState: previousState
                });
            } else {
                // This was a create operation
                addToUndoHistory({
                    type: 'create',
                    room: updatedRoom
                });
            }
            
            // Update reciprocal exits in connected rooms
            for (const update of roomsToUpdate) {
                const targetRoom = update.room;
                const newExits = { ...(targetRoom.exits || {}) };
                
                if (update.add) {
                    // Add reciprocal exit
                    newExits[update.direction] = update.targetRoomId;
                } else {
                    // Remove reciprocal exit
                    delete newExits[update.direction];
                }
                
                try {
                    targetRoom.exits = newExits;
                    await updateRoom(targetRoom.id, targetRoom);
                } catch (error) {
                    console.error('Error updating reciprocal exit:', error);
                }
            }
            
            roomModal.hide();
            setRooms(await fetchRooms()); // Reload rooms
            renderMap(); // Redraw entire map with all connection lines
            
            // Update selectedRoom reference after reload
            if (selectedRoom) {
                setSelectedRoom(rooms.find(r => r.id === selectedRoom.id) || selectedRoom);
            }
            updateSelectionDisplay();
        } else {
            alert('Error saving room');
        }
    } catch (error) {
        console.error('Error saving room:', error);
        alert('Error saving room');
    }
}

// Delete room
export async function deleteRoom() {

    if (!selectedRoom) return;
    
    if (confirm('Are you sure you want to delete this room?')) {
        // Save room state before deleting
        const roomToDelete = JSON.parse(JSON.stringify(selectedRoom));
        
        try {
            await APIDeleteRoom(selectedRoom.id);
            addToUndoHistory({
                type: 'delete',
                room: roomToDelete
            });
            
            roomModal.hide();
            setRooms(await fetchRooms()); // Reload rooms
            renderMap(); // Redraw entire map
        } catch (error) {
            console.error('Error deleting room:', error);
            alert('Error deleting room');
        }
    }
}

// Create area
export async function saveArea(areaData) {
    await createArea(areaData);
    // ...refresh areas and UI...
}

// Exit management stubs
export function handleExitChange(direction, isChecked) {
    // ...handle exit checkbox change...
}

export function selectAllExits() {
    // ...select all exits...
}

export function clearAllExits() {
    // ...clear all exits...
}

export function autoSelectExits() {
    // ...auto select exits where adjacent rooms exist...
}

export async function saveMap() {
    try {
        const allRooms = await fetchRooms();
        
        // Convert to rooms.json format
        const roomsData = {
            rooms: {}
        };
        
        allRooms.forEach(room => {
            roomsData.rooms[room.room_id] = {
                room_id: room.room_id,
                area_id: room.area_id ? areas.find(a => a.id === room.area_id)?.area_id : null,
                x_coord: room.x,
                y_coord: room.y,
                z_coord: room.z,
                name: room.name,
                description: room.description,
                short_description: room.description,
                exits: room.exits || {},
                items: [],
                npcs: [],
                lighting: 'normal',
                temperature: 'normal',
                weather_effects: [],
                is_safe: false,
                is_indoors: false,
                is_water: false,
                is_air: false
            };
        });
        
        // Create download
        const dataStr = JSON.stringify(roomsData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `rooms_export_${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        alert(`Map exported successfully! ${allRooms.length} rooms saved.`);
    } catch (error) {
        console.error('Error saving map:', error);
        alert('Error exporting map');
    }
}

export function editDoor(direction) {
    if (!selectedRoom) {
        alert('Please select a room first');
        return;
    }
    
    currentDoorDirection = direction;
    document.getElementById('doorDirection').textContent = direction.toUpperCase();
    
    // Populate key select
    populateKeySelect();
    
    // Load existing door data if it exists
    const existingDoor = selectedRoom.doors && selectedRoom.doors[direction];
    
    if (existingDoor) {
        // Edit existing door
        document.getElementById('doorId').value = existingDoor.door_id || '';
        document.getElementById('doorName').value = existingDoor.name || '';
        document.getElementById('doorDescription').value = existingDoor.description || '';
        document.getElementById('doorKeyId').value = existingDoor.key_id || '';
        document.getElementById('doorLockDifficulty').value = existingDoor.lock_difficulty || 0;
        updateLockDifficultyLabel();
        
        // Set flags
        const flags = existingDoor.flags || [];
        document.getElementById('flagClosed').checked = flags.includes('closed');
        document.getElementById('flagLocked').checked = flags.includes('locked');
        document.getElementById('flagPickProof').checked = flags.includes('pick_proof');
        document.getElementById('flagPassProof').checked = flags.includes('pass_proof');
        document.getElementById('flagSecret').checked = flags.includes('secret');
        document.getElementById('flagHidden').checked = flags.includes('hidden');
        document.getElementById('flagNoLock').checked = flags.includes('no_lock');
        document.getElementById('flagNoKnock').checked = flags.includes('no_knock');
        document.getElementById('flagNoClose').checked = flags.includes('no_close');
        
        document.getElementById('deleteDoorBtn').style.display = 'inline-block';
    } else {
        // New door - generate default ID
        const defaultDoorId = `door_${selectedRoom.room_id}_${direction}`;
        document.getElementById('doorId').value = defaultDoorId;
        document.getElementById('doorName').value = '';
        document.getElementById('doorDescription').value = '';
        document.getElementById('doorKeyId').value = '';
        document.getElementById('doorLockDifficulty').value = 0;
        updateLockDifficultyLabel();
        
        // Clear all flags
        document.getElementById('flagClosed').checked = false;
        document.getElementById('flagLocked').checked = false;
        document.getElementById('flagPickProof').checked = false;
        document.getElementById('flagPassProof').checked = false;
        document.getElementById('flagSecret').checked = false;
        document.getElementById('flagHidden').checked = false;
        document.getElementById('flagNoLock').checked = false;
        document.getElementById('flagNoKnock').checked = false;
        document.getElementById('flagNoClose').checked = false;
        
        document.getElementById('deleteDoorBtn').style.display = 'none';
    }
    
    doorModal.show();
}

export function updateLockDifficultyLabel() {
    const difficulty = document.getElementById('doorLockDifficulty').value;
    let label = difficulty;
    
    if (difficulty == 0) {
        label += ' (No Lock)';
    } else if (difficulty <= 25) {
        label += ' (Trivial)';
    } else if (difficulty <= 50) {
        label += ' (Easy)';
    } else if (difficulty <= 75) {
        label += ' (Medium)';
    } else if (difficulty <= 100) {
        label += ' (Hard)';
    } else if (difficulty <= 150) {
        label += ' (Magical)';
    } else if (difficulty <= 200) {
        label += ' (Very Magical)';
    } else {
        label += ' (Nearly Impossible)';
    }
    
    document.getElementById('lockDifficultyValue').textContent = label;
}

export async function saveDoor() {
    if (!selectedRoom || !currentDoorDirection) {
        alert('No room or direction selected');
        return;
    }
    
    // Collect door data
    const doorData = {
        door_id: document.getElementById('doorId').value.trim(),
        name: document.getElementById('doorName').value.trim(),
        description: document.getElementById('doorDescription').value.trim(),
        key_id: document.getElementById('doorKeyId').value,
        lock_difficulty: parseInt(document.getElementById('doorLockDifficulty').value),
        flags: []
    };
    
    // Collect flags
    if (document.getElementById('flagClosed').checked) doorData.flags.push('closed');
    if (document.getElementById('flagLocked').checked) doorData.flags.push('locked');
    if (document.getElementById('flagPickProof').checked) doorData.flags.push('pick_proof');
    if (document.getElementById('flagPassProof').checked) doorData.flags.push('pass_proof');
    if (document.getElementById('flagSecret').checked) doorData.flags.push('secret');
    if (document.getElementById('flagHidden').checked) doorData.flags.push('hidden');
    if (document.getElementById('flagNoLock').checked) doorData.flags.push('no_lock');
    if (document.getElementById('flagNoKnock').checked) doorData.flags.push('no_knock');
    if (document.getElementById('flagNoClose').checked) doorData.flags.push('no_close');
    
    // Validate required fields
    if (!doorData.door_id) {
        alert('Door ID is required');
        return;
    }
    
    if (!doorData.name) {
        alert('Door name is required');
        return;
    }
    
    // Validate locked doors have keys
    if (doorData.flags.includes('locked') && !doorData.key_id) {
        alert('Locked doors must have a key assigned!');
        return;
    }
    
    // Validate conflicting flags
    if (doorData.flags.includes('no_lock') && doorData.flags.includes('locked')) {
        alert('Door cannot have both "No Lock" and "Locked" flags');
        return;
    }
    
    if (doorData.flags.includes('no_close') && doorData.flags.includes('closed')) {
        alert('Door cannot have both "No Close" and "Closed" flags');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/rooms/${selectedRoom.id}/doors/${currentDoorDirection}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(doorData)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            alert(`Error: ${result.error}\n${result.details ? result.details.join('\n') : ''}`);
            return;
        }
        
        // Update local room data
        if (!selectedRoom.doors) {
            selectedRoom.doors = {};
        }
        selectedRoom.doors[currentDoorDirection] = doorData;
        
        // Update the door button appearance
        updateDoorButtons();
        
        doorModal.hide();
        alert(`Door saved successfully for ${currentDoorDirection} direction`);
    } catch (error) {
        console.error('Error saving door:', error);
        alert('Error saving door');
    }
}

export async function deleteDoor() {
    if (!selectedRoom || !currentDoorDirection) {
        alert('No room or direction selected');
        return;
    }
    
    if (!confirm(`Delete the ${currentDoorDirection} door?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/rooms/${selectedRoom.id}/doors/${currentDoorDirection}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            alert(`Error: ${result.error}`);
            return;
        }
        
        // Remove from local room data
        if (selectedRoom.doors && selectedRoom.doors[currentDoorDirection]) {
            delete selectedRoom.doors[currentDoorDirection];
        }
        
        // Update the door button appearance
        updateDoorButtons();
        
        doorModal.hide();
        alert('Door deleted successfully');
    } catch (error) {
        console.error('Error deleting door:', error);
        alert('Error deleting door');
    }
}

export function updateDoorButtons() {
    const directions = ['north', 'south', 'east', 'west', 'up', 'down'];
    
    directions.forEach(direction => {
        const button = document.querySelector(`button[onclick="editDoor('${direction}')"]`);
        if (button) {
            if (selectedRoom.doors && selectedRoom.doors[direction]) {
                button.classList.remove('btn-outline-warning');
                button.classList.add('btn-warning');
                button.innerHTML = `<i class="fas fa-door-closed"></i> ${direction.charAt(0).toUpperCase() + direction.slice(1)} Door ✓`;
            } else {
                button.classList.remove('btn-warning');
                button.classList.add('btn-outline-warning');
                button.innerHTML = `<i class="fas fa-door-closed"></i> ${direction.charAt(0).toUpperCase() + direction.slice(1)} Door`;
            }
        }
    });
}

export function showDoorHelp() {
    const helpText = `Door System Help:

Lock Difficulty:
- 0: No lock
- 1-100: Normal locks (pickable by thieves)
- 101-255: Magical locks (wizard lock spell)

Door Flags:
- Closed: Door starts closed
- Locked: Door is locked (requires key)
- Pick Proof: Cannot be picked by thieves
- Pass Proof: Cannot pass through at all
- Secret: Hidden door (requires search)
- Hidden: Not visible in room description
- No Lock: Door cannot be locked
- No Knock: Knock spell won't work
- No Close: Door cannot be closed

Important: Locked doors MUST have a key assigned!`;
    
    alert(helpText);
}

let availableKeys = [];

export async function loadKeys() {
    try {
        const response = await fetch(`${API_BASE}/api/keys`);
        availableKeys = await response.json();
        console.log('Loaded keys:', availableKeys.length);
    } catch (error) {
        console.error('Error loading keys:', error);
        availableKeys = [];
    }
}

export function populateKeySelect() {
    const keySelect = document.getElementById('doorKeyId');
    keySelect.innerHTML = '<option value="">No Key Required</option>';
    
    availableKeys.forEach(key => {
        const option = document.createElement('option');
        option.value = key.template_id;
        option.textContent = `${key.name} (${key.template_id})`;
        keySelect.appendChild(option);
    });
}