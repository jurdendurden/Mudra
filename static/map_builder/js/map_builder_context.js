// map_builder_context.js
// Context menu logic, keyboard shortcuts, batch actions
import { rooms, selectedRoom, multiSelectedRooms, CANVAS_CENTER, GRID_SIZE } from './map_builder_core.js';
import { updateMultiSelection, clearMultiSelection } from './map_builder_canvas.js';
import { renderMap, updateSelectionDisplay, updateAutoRoomToggle } from './map_builder_render.js';

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
                multiSelectedRooms.length = 0;
                multiSelectedRooms.push(clickedRoom.id);
                window.selectedRoom = clickedRoom;
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
        if (multiSelectedRooms.length > 0) {
            deleteSelectedRooms();
        } else if (selectedRoom) {
            if (typeof deleteSingleSelectedRoom === 'function') deleteSingleSelectedRoom();
        }
    }
    // Numpad handling for Auto Room mode
    if (window.autoRoomMode && selectedRoom && multiSelectedRooms.length <= 1) {
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
            await fetch('/api/rooms', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newRoomData)
            });
        } catch (error) {
            console.error('Error copying room:', error);
        }
    }
    if (typeof loadRooms === 'function') await loadRooms();
    renderMap();
    clearMultiSelection();
// End of copySelectedRooms
}

export async function deleteSelectedRooms() {
    if (multiSelectedRooms.length === 0) {
        alert('No rooms selected');
        return;
    }
    if (!confirm(`Are you sure you want to delete ${multiSelectedRooms.length} room(s)?`)) {
        return;
    }
    for (const roomId of multiSelectedRooms) {
        try {
            await fetch(`/api/rooms/${roomId}`, {
                method: 'DELETE'
            });
        } catch (error) {
            console.error('Error deleting room:', error);
        }
    }
    if (typeof loadRooms === 'function') await loadRooms();
    renderMap();
    clearMultiSelection();
// End of deleteSelectedRooms
}

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
            await fetch(`/api/rooms/${room.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    room_id: room.room_id,
                    name: room.name,
                    description: room.description,
                    area_id: room.area_id,
                    x: room.x,
                    y: room.y,
                    z: room.z || 0,
                    exits: newExits
                })
            });
            for (const update of roomsToUpdate) {
                const targetRoom = update.room;
                const newTargetExits = { ...(targetRoom.exits || {}) };
                if (!newTargetExits[update.direction]) {
                    newTargetExits[update.direction] = update.targetRoomId;
                    totalExitsAdded++;
                }
                try {
                    await fetch(`/api/rooms/${targetRoom.id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            room_id: targetRoom.room_id,
                            name: targetRoom.name,
                            description: targetRoom.description,
                            area_id: targetRoom.area_id,
                            x: targetRoom.x,
                            y: targetRoom.y,
                            z: targetRoom.z || 0,
                            exits: newTargetExits
                        })
                    });
                } catch (error) {
                    console.error('Error updating reciprocal exit:', error);
                }
            }
        } catch (error) {
            console.error(`Error auto-exiting room ${room.room_id}:`, error);
        }
    }
    if (typeof loadRooms === 'function') await loadRooms();
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
            await fetch(`/api/rooms/${room.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ...room,
                    name: newName
                })
            });
        } catch (error) {
            console.error('Error changing room name:', error);
        }
    }
    if (typeof loadRooms === 'function') await loadRooms();
    renderMap();
    clearMultiSelection();
// End of changeSelectedRoomNames
}
