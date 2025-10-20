// map_builder_room_editor.js
// Room/area modal logic, exit management, dropdown population
import { areas, rooms, selectedRoom, roomModal, setSelectedRoom, setRooms, CANVAS_CENTER, CANVAS_PADDING, GRID_SIZE } from './map_builder_core.js';
import { createRoom, updateRoom, deleteRoom, createArea, fetchRooms } from './map_builder_api.js';
import { renderMap, renderAreaList, renderRoomList } from './map_builder_render.js';

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
        option.value = area.area_id;
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

// Save room (create or update)
export async function saveRoom(roomData) {
    let newRoom = null;
    if (roomData.id) {
        newRoom = await updateRoom(roomData.id, roomData);
    } else {
        newRoom = await createRoom(roomData);
    }

    if (newRoom != null) {    
    // Add exit from current room to new room
    const updatedExits = { ...(selectedRoom.exits || {}) };
    updatedExits[direction.name] = newRoom.room_id;
    
    // Update current room with new exit
    await fetch(`/api/rooms/${selectedRoom.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            room_id: selectedRoom.room_id,
            name: selectedRoom.name,
            description: selectedRoom.description,
            area_id: selectedRoom.area_id,
            x: selectedRoom.x,
            y: selectedRoom.y,
            z: selectedRoom.z || 0,
            exits: updatedExits,
            lighting: selectedRoom.lighting || 'normal'
        })
    });
    
    // Reload rooms and re-render
    setRooms(await fetchRooms());
    renderMap();
    
    // Select the newly created room to continue walking
    const freshNewRoom = rooms.find(r => r.room_id === newRoom.room_id);
    if (freshNewRoom) {
        selectedRoom = freshNewRoom;
        
        // Highlight the new room
        const nodes = document.querySelectorAll('.room-node');
        nodes.forEach(n => {
            n.classList.remove('selected');
            if (n.innerHTML.includes(freshNewRoom.name) && 
                n.style.left === `${freshNewRoom.x * GRID_SIZE + CANVAS_CENTER + CANVAS_PADDING}px` &&
                n.style.top === `${-freshNewRoom.y * GRID_SIZE + CANVAS_CENTER + CANVAS_PADDING}px`) {
                n.classList.add('selected');
            }
        });
        
        updateSelectionDisplay();
    }
    
    console.log(`✓ Created room ${newRoom.room_id} at (${newX}, ${newY}, ${newZ})`);
    // ...refresh rooms and UI...
}
}
// Delete room
export async function deleteRoomById(roomId) {
    await deleteRoom(roomId);
    // ...refresh rooms and UI...
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
