// map_builder_room_editor.js
// Room/area modal logic, exit management, dropdown population
import { areas, rooms, selectedRoom, roomModal, setSelectedRoom, setRooms, CANVAS_CENTER, CANVAS_PADDING, GRID_SIZE } from './map_builder_core.js';
import { createRoom, updateRoom, deleteRoom as APIDeleteRoom, createArea, fetchRooms } from './map_builder_api.js';
import { renderMap, renderAreaList, renderRoomList, updateSelectionDisplay } from './map_builder_render.js';
import { addToUndoHistory } from './map_builder_undo.js';

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
                    // await fetch(`${API_BASE}/api/rooms/${targetRoom.id}`, {
                    //     method: 'PUT',
                    //     headers: {
                    //         'Content-Type': 'application/json'
                    //     },
                    //     body: JSON.stringify({
                    //         room_id: targetRoom.room_id,
                    //         name: targetRoom.name,
                    //         description: targetRoom.description,
                    //         area_id: targetRoom.area_id,
                    //         x: targetRoom.x,
                    //         y: targetRoom.y,
                    //         z: targetRoom.z || 0,
                    //         exits: newExits
                    //     })
                    // });
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
// // Save room (create or update)
// export async function saveRoom(roomData) {
//     let newRoom = null;
//     if (roomData.id) {
//         newRoom = await updateRoom(roomData.id, roomData);
//     } else {
//         newRoom = await createRoom(roomData);
//     }

//     if (newRoom != null) {    
//     // Add exit from current room to new room
//     const updatedExits = { ...(selectedRoom.exits || {}) };
//     updatedExits[direction.name] = newRoom.room_id;
    
//     // Update current room with new exit
//     await fetch(`/api/rooms/${selectedRoom.id}`, {
//         method: 'PUT',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify({
//             room_id: selectedRoom.room_id,
//             name: selectedRoom.name,
//             description: selectedRoom.description,
//             area_id: selectedRoom.area_id,
//             x: selectedRoom.x,
//             y: selectedRoom.y,
//             z: selectedRoom.z || 0,
//             exits: updatedExits,
//             lighting: selectedRoom.lighting || 'normal'
//         })
//     });
    
//     // Reload rooms and re-render
//     setRooms(await fetchRooms());
//     renderMap();
    
//     // Select the newly created room to continue walking
//     const freshNewRoom = rooms.find(r => r.room_id === newRoom.room_id);
//     if (freshNewRoom) {
//         selectedRoom = freshNewRoom;
        
//         // Highlight the new room
//         const nodes = document.querySelectorAll('.room-node');
//         nodes.forEach(n => {
//             n.classList.remove('selected');
//             if (n.innerHTML.includes(freshNewRoom.name) && 
//                 n.style.left === `${freshNewRoom.x * GRID_SIZE + CANVAS_CENTER + CANVAS_PADDING}px` &&
//                 n.style.top === `${-freshNewRoom.y * GRID_SIZE + CANVAS_CENTER + CANVAS_PADDING}px`) {
//                 n.classList.add('selected');
//             }
//         });
        
//         updateSelectionDisplay();
//     }
    
//     console.log(`✓ Created room ${newRoom.room_id} at (${newX}, ${newY}, ${newZ})`);
//     // ...refresh rooms and UI...
// }
// }
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