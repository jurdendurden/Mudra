// map_builder_context.js
// Context menu logic, keyboard shortcuts, batch actions
import { rooms, selectedRoom, multiSelectedRooms, setMultiSelectedRooms, setSelectedRoom, autoRoomMode, setRooms, CANVAS_CENTER, CANVAS_PADDING, GRID_SIZE } from './map_builder_core.js';
import { updateMultiSelection, clearMultiSelection } from './map_builder_canvas.js';
import { renderMap, updateSelectionDisplay, updateAutoRoomToggle } from './map_builder_render.js';
import { getNextRoomId } from './map_builder_utils.js';
import { fetchRooms, createRoom, updateRoom, deleteRoom } from './map_builder_api.js';
import { addToUndoHistory, undoLastAction, updateUndoButton } from './map_builder_undo.js';
import { saveRoom } from './map_builder_room_editor.js';

// Context menu
export function handleContextMenu(event) {
    const target = event.target;
    const isRoomNode = target.classList.contains('room-node') || target.closest('.room-node');
    if (isRoomNode) {
        event.preventDefault();
        const roomNode = target.classList.contains('room-node') ? target : target.closest('.room-node');
        const nodeLeft = parseInt(roomNode.style.left);
        const nodeTop = parseInt(roomNode.style.top);
        const clickedRoom = rooms.find(r => 
            r.x * GRID_SIZE + CANVAS_CENTER + 10 === nodeLeft && 
            -r.y * GRID_SIZE + CANVAS_CENTER + 10 === nodeTop
        );
        if (clickedRoom) {
            if (!multiSelectedRooms.includes(clickedRoom.id)) {
                setMultiSelectedRooms([clickedRoom.id]);
                setSelectedRoom(clickedRoom);
                updateMultiSelection();
            }
            const contextMenu = document.getElementById('contextMenu');
            contextMenu.style.display = 'block';
            contextMenu.style.left = event.pageX + 'px';
            contextMenu.style.top = event.pageY + 'px';
        }
    }
// End of handleContextMenu
}

export function hideContextMenu() {
    const contextMenu = document.getElementById('contextMenu');
    if (contextMenu) contextMenu.style.display = 'none';
// End of hideContextMenu
}

export async function createAutoRoom(direction) {
    if (!selectedRoom) return;
    
    const newX = selectedRoom.x + direction.x;
    const newY = selectedRoom.y + direction.y;
    const newZ = (selectedRoom.z || 0) + direction.z;
    
    // Check if room already exists at target location
    const existingRoom = rooms.find(r => 
        r.x === newX && r.y === newY && (r.z || 0) === newZ
    );
    
    if (existingRoom) {
        console.log(`❌ Room already exists at (${newX}, ${newY}, ${newZ}). Cannot create.`);
        console.log(`   Existing room: ${existingRoom.room_id} - ${existingRoom.name}`);
        
        // Briefly flash the existing room
        const nodes = document.querySelectorAll('.room-node');
        nodes.forEach(n => {
            if (n.innerHTML.includes(existingRoom.name) && 
                n.style.left === `${existingRoom.x * GRID_SIZE + CANVAS_CENTER + CANVAS_PADDING}px` &&
                n.style.top === `${-existingRoom.y * GRID_SIZE + CANVAS_CENTER + CANVAS_PADDING}px`) {
                // Flash the node
                n.style.backgroundColor = '#e74c3c';
                n.style.transform = 'scale(1.2)';
                setTimeout(() => {
                    n.style.backgroundColor = '';
                    n.style.transform = '';
                }, 300);
            }
        });
        
        return;
    }

    // Generate new room ID
    const nextRoomId = getNextRoomId();
    
    // Create room data
    const roomData = {
        room_id: nextRoomId,
        name: `Room ${nextRoomId}`,
        description: `A room ${direction.name} of ${selectedRoom.name}.`,
        area_id: selectedRoom.area_id || null,
        x: newX,
        y: newY,
        z: newZ,
        exits: {},
        lighting: selectedRoom.lighting || 'normal'
    };
    
    // Determine the opposite direction for reciprocal exit
    const oppositeDirections = {
        'north': 'south',
        'south': 'north',
        'east': 'west',
        'west': 'east',
        'northeast': 'southwest',
        'northwest': 'southeast',
        'southeast': 'northwest',
        'southwest': 'northeast',
        'up': 'down',
        'down': 'up'
    };
    
    const oppositeDir = oppositeDirections[direction.name];
    
    // Add exit from new room back to current room
    if (oppositeDir) {
        roomData.exits[oppositeDir] = selectedRoom.room_id;
    }
    
    try {
        // Create the new room
        const newRoom = await createRoom(roomData);
        // Add exit from current room to new room
        const updatedExits = { ...(selectedRoom.exits || {}) };
        updatedExits[direction.name] = newRoom.room_id;
        // Update current room with new exit
        await updateRoom(selectedRoom.id, {
            room_id: selectedRoom.room_id,
            name: selectedRoom.name,
            description: selectedRoom.description,
            area_id: selectedRoom.area_id,
            x: selectedRoom.x,
            y: selectedRoom.y,
            z: selectedRoom.z || 0,
            exits: updatedExits,
            lighting: selectedRoom.lighting || 'normal'
        });
        // Reload rooms and re-render
        setRooms(await fetchRooms());
        renderMap();
        // Select the newly created room to continue walking
        const freshNewRoom = rooms.find(r => r.room_id === newRoom.room_id);
        if (freshNewRoom) {
            setSelectedRoom(freshNewRoom);
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
    } catch (error) {
        console.error('❌ Error creating auto room:', error);
        alert('Error creating auto room: ' + error.message);
    }
}
// Keyboard shortcuts
export function handleKeyPress(event) {
    if (event.key === 'Enter' && (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA')) {
        const modal = document.getElementById('roomModal');
        if (modal && modal.classList.contains('show')) {
            event.preventDefault();
            if (typeof saveRoom === 'function') saveRoom();
            return;
        }
    }
    if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') return;
    if (event.key === 'Escape') {
        clearMultiSelection();
        return;
    }
    if (event.ctrlKey && event.key === 'z') {
        event.preventDefault();
        if (typeof undoLastAction === 'function') undoLastAction();
        return;
    }
    if (event.key === 'Delete') {
        deleteSelectedRooms();
        return;
    }
    // Numpad handling for Auto Room mode
    // Create a room in the given direction using Auto Room mode
    
    if (autoRoomMode && selectedRoom && multiSelectedRooms.length <= 1) {
        const numpadCodeMap = {
            'Numpad8': { x: 0, y: 1, z: 0, name: 'north' },
            'Numpad2': { x: 0, y: -1, z: 0, name: 'south' },
            'Numpad6': { x: 1, y: 0, z: 0, name: 'east' },
            'Numpad4': { x: -1, y: 0, z: 0, name: 'west' },
            'Numpad9': { x: 1, y: 1, z: 0, name: 'northeast' },
            'Numpad7': { x: -1, y: 1, z: 0, name: 'northwest' },
            'Numpad3': { x: 1, y: -1, z: 0, name: 'southeast' },
            'Numpad1': { x: -1, y: -1, z: 0, name: 'southwest' },
            'NumpadAdd': { x: 0, y: 0, z: 1, name: 'up' },
            'NumpadSubtract': { x: 0, y: 0, z: -1, name: 'down' }
        };
        const keyMap = {
            '8': { x: 0, y: 1, z: 0, name: 'north' },
            '2': { x: 0, y: -1, z: 0, name: 'south' },
            '6': { x: 1, y: 0, z: 0, name: 'east' },
            '4': { x: -1, y: 0, z: 0, name: 'west' },
            '9': { x: 1, y: 1, z: 0, name: 'northeast' },
            '7': { x: -1, y: 1, z: 0, name: 'northwest' },
            '3': { x: 1, y: -1, z: 0, name: 'southeast' },
            '1': { x: -1, y: -1, z: 0, name: 'southwest' },
            '+': { x: 0, y: 0, z: 1, name: 'up' },
            '-': { x: 0, y: 0, z: -1, name: 'down' }
        };
        let direction = null;
        if (event.code && numpadCodeMap[event.code]) {
            direction = numpadCodeMap[event.code];
        } else if (keyMap[event.key]) {
            direction = keyMap[event.key];
        }
        if (direction && typeof createAutoRoom === 'function') {
            event.preventDefault();
            createAutoRoom(direction);
            return;
        }
    }
// End of handleKeyPress
}

// Batch actions
export async function copySelectedRooms() {
    if (multiSelectedRooms.length === 0) {
        alert('No rooms selected');
        return;
    }
    const offset = prompt('Enter offset for copied rooms (format: x,y,z)', '1,0,0');
    if (!offset) return;
    const [dx, dy, dz] = offset.split(',').map(n => parseInt(n.trim()));
    if (isNaN(dx) || isNaN(dy) || isNaN(dz)) {
        alert('Invalid offset format. Use: x,y,z');
        return;
    }
    for (const roomId of multiSelectedRooms) {
        const room = rooms.find(r => r.id === roomId);
        if (!room) continue;
        const nextRoomId = typeof getNextRoomId === 'function' ? getNextRoomId() : `room_${Math.random().toString(36).substr(2, 5)}`;
        const newRoomData = {
            room_id: nextRoomId,
            name: room.name + ' (Copy)',
            description: room.description,
            area_id: room.area_id,
            x: room.x + dx,
            y: room.y + dy,
            z: (room.z || 0) + dz,
            exits: {}
        };
        try {
            await createRoom(newRoomData);
        } catch (error) {
            console.error('Error copying room:', error);
        }
    }
    if (typeof fetchRooms === 'function') setRooms(await fetchRooms());
    renderMap();
    clearMultiSelection();
// End of copySelectedRooms
}

export async function deleteSelectedRooms() {
    if (selectedRoom === null && multiSelectedRooms.length === 0) {
        alert('No rooms selected');
        return;
    }
    if ((multiSelectedRooms.length <= 1 && selectedRoom != null && !confirm(`Are you sure you want to delete the room "${selectedRoom.name}"?`)) 
        || (multiSelectedRooms.length > 1 && !confirm(`Are you sure you want to delete ${multiSelectedRooms.length} room(s)?`))) {
        return;
    }

    if(multiSelectedRooms.length > 1) {
        const errorRooms = [];
        for (const roomId of multiSelectedRooms) {
            try {
                let roomToDelete = rooms.find(r => r.id == roomId);
                if(roomToDelete) {
                    addToUndoHistory({
                        type: 'delete',
                        room: roomToDelete
                    });
                    await deleteRoom(roomId);
                }
            } catch (error) {
                errorRooms.push(roomId);
                console.error('Error deleting room:', error);
            }
        }
        if(errorRooms.length > 0) {
            alert(`Error deleting the following rooms: ${errorRooms.join(', ')}`);
        }
    }
    else if(selectedRoom !== null || multiSelectedRooms.length === 1) {
        if(selectedRoom === null) {
            setSelectedRoom(rooms.find(r => r.id === multiSelectedRooms[0]));
        }
        try {
            addToUndoHistory({
                    type: 'delete',
                    room: selectedRoom
                });
            await deleteRoom(selectedRoom.id);
        } catch (error) {
            console.error('Error deleting room:', error);
            alert(`Error deleting room: ${error.message}`);
        }
    }

    if (typeof fetchRooms === 'function') {
        setRooms(await fetchRooms());
    }
    renderMap();
    clearMultiSelection();
} // End of deleteSelectedRooms

export async function autoExitSelectedRooms() {
    if (multiSelectedRooms.length === 0) {
        alert('No rooms selected');
        return;
    }
    if (!confirm(`Auto-detect and set exits for ${multiSelectedRooms.length} selected room(s)?`)) {
        return;
    }
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
    let totalExitsAdded = 0;
    for (const roomId of multiSelectedRooms) {
        const room = rooms.find(r => r.id === roomId);
        if (!room) continue;
        const newExits = { ...(room.exits || {}) };
        const roomsToUpdate = [];
        for (const [direction, offset] of Object.entries(directionOffsets)) {
            if (newExits[direction]) continue;
            const targetX = room.x + offset.x;
            const targetY = room.y + offset.y;
            const targetZ = (room.z || 0) + offset.z;
            const targetRoom = rooms.find(r => r.x === targetX && r.y === targetY && (r.z || 0) === targetZ);
            if (targetRoom) {
                newExits[direction] = targetRoom.room_id;
                totalExitsAdded++;
                const oppositeDir = oppositeDirections[direction];
                if (!targetRoom.exits || !targetRoom.exits[oppositeDir]) {
                    roomsToUpdate.push({
                        room: targetRoom,
                        direction: oppositeDir,
                        targetRoomId: room.room_id
                    });
                }
            }
        }
        try {
            await updateRoom(room.id, {
                room_id: room.room_id,
                name: room.name,
                description: room.description,
                area_id: room.area_id,
                x: room.x,
                y: room.y,
                z: room.z || 0,
                exits: newExits
            });
            for (const update of roomsToUpdate) {
                const targetRoom = update.room;
                const newTargetExits = { ...(targetRoom.exits || {}) };
                if (!newTargetExits[update.direction]) {
                    newTargetExits[update.direction] = update.targetRoomId;
                    totalExitsAdded++;
                }
                try {
                    await updateRoom(targetRoom.id, {
                        room_id: targetRoom.room_id,
                        name: targetRoom.name,
                        description: targetRoom.description,
                        area_id: targetRoom.area_id,
                        x: targetRoom.x,
                        y: targetRoom.y,
                        z: targetRoom.z || 0,
                        exits: newTargetExits
                    });
                } catch (error) {
                    console.error('Error updating reciprocal exit:', error);
                }
            }
        } catch (error) {
            console.error(`Error auto-exiting room ${room.room_id}:`, error);
        }
    }
    if (typeof fetchRooms === 'function') setRooms(await fetchRooms());
    renderMap();
    clearMultiSelection();
    if (totalExitsAdded > 0) {
        alert(`Auto-exit complete! Added ${totalExitsAdded} new exit(s) to ${multiSelectedRooms.length} room(s). Existing exits were preserved.`);
    } else {
        alert(`Auto-exit complete! No new exits added - all adjacent exits already exist.`);
    }
// End of autoExitSelectedRooms
}

export async function changeSelectedRoomNames() {
    hideContextMenu();
    const roomsToChange = multiSelectedRooms.length > 0 
        ? multiSelectedRooms.map(id => rooms.find(r => r.id === id)).filter(r => r)
        : [];
    if (roomsToChange.length === 0) {
        alert('No rooms selected');
        return;
    }
    const newName = prompt('Enter new name for selected room(s):');
    if (!newName) return;
    for (const room of roomsToChange) {
        try {
            await updateRoom(room.id, {
                ...room,
                name: newName
            });
        } catch (error) {
            console.error('Error changing room name:', error);
        }
    }
    if (typeof fetchRooms === 'function') setRooms(await fetchRooms());
    renderMap();
    clearMultiSelection();
// End of changeSelectedRoomNames
}
