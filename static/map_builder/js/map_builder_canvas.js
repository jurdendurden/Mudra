// map_builder_canvas.js
// Canvas interaction: drag-and-drop, selection, mouse/keyboard events, coordinate display
import { rooms, selectedRoom, multiSelectedRooms, isSelecting, selectionStart, selectionBox, isDraggingRoom, draggedRoom, draggedNode, draggedRooms, draggedNodes, dragOffset, CANVAS_CENTER, GRID_SIZE } from './map_builder_core.js';
import { renderMap } from './map_builder_render.js';

// Handle room drag start
export function handleRoomDragStart(event, room, node) {
    // Only allow drag with Ctrl key held
    if (event.ctrlKey) {
        event.preventDefault();
        event.stopPropagation();
        isDraggingRoom = true;
        draggedRoom = room;
        draggedNode = node;
        const nodeRect = node.getBoundingClientRect();
        dragOffset = {
            x: event.clientX - nodeRect.left,
            y: event.clientY - nodeRect.top
        };
        // Hide tooltip during drag
        if (typeof hideTooltip === 'function') hideTooltip();
        // Check if this room is part of a multi-selection
        if (multiSelectedRooms.includes(room.id)) {
            draggedRooms = multiSelectedRooms.map(roomId => rooms.find(r => r.id === roomId)).filter(r => r);
            draggedNodes = [];
            const allNodes = document.querySelectorAll('.room-node');
            allNodes.forEach(n => {
                const nodeLeft = parseInt(n.style.left);
                const nodeTop = parseInt(n.style.top);
                const matchingRoom = draggedRooms.find(r => 
                    r.x * GRID_SIZE + CANVAS_CENTER + 10 === nodeLeft && 
                    -r.y * GRID_SIZE + CANVAS_CENTER + 10 === nodeTop
                );
                if (matchingRoom) {
                    draggedNodes.push({ node: n, room: matchingRoom });
                    n.style.cursor = 'grabbing';
                }
            });
        } else {
            draggedRooms = [room];
            draggedNodes = [{ node: node, room: room }];
            node.style.cursor = 'grabbing';
        }
    }
// End of handleRoomDragStart
}

// Handle room drop
export async function handleRoomDrop(event) {
    if (!isDraggingRoom || !draggedRoom || !draggedNode) return;
    window.justFinishedDrag = true;
    const canvas = document.getElementById('map-canvas');
    const rect = canvas.getBoundingClientRect();
    const dropX = event.clientX - rect.left + canvas.scrollLeft;
    const dropY = event.clientY - rect.top + canvas.scrollTop;
    const newGridX = Math.round((dropX - dragOffset.x - CANVAS_CENTER) / GRID_SIZE);
    const newGridY = Math.round(-(dropY - dragOffset.y - CANVAS_CENTER) / GRID_SIZE);
    const deltaX = newGridX - draggedRoom.x;
    const deltaY = newGridY - draggedRoom.y;
    let hasConflict = false;
    for (const roomToMove of draggedRooms) {
        const targetX = roomToMove.x + deltaX;
        const targetY = roomToMove.y + deltaY;
        const targetZ = roomToMove.z || 0;
        const existingRoom = rooms.find(r => 
            !draggedRooms.find(dr => dr.id === r.id) &&
            r.x === targetX && r.y === targetY && (r.z || 0) === targetZ
        );
        if (existingRoom) {
            alert(`Cannot move rooms: position (${targetX}, ${targetY}, ${targetZ}) is occupied by ${existingRoom.name}`);
            hasConflict = true;
            break;
        }
    }
    if (!hasConflict) {
        if (draggedRooms.length === 1) {
            const newX = draggedRooms[0].x + deltaX;
            const newY = draggedRooms[0].y + deltaY;
            const newZ = draggedRooms[0].z || 0;
            if (typeof updateRoomPosition === 'function') await updateRoomPosition(draggedRooms[0], newX, newY, newZ);
        } else {
            for (const roomToMove of draggedRooms) {
                const newX = roomToMove.x + deltaX;
                const newY = roomToMove.y + deltaY;
                const newZ = roomToMove.z || 0;
                try {
                    await fetch(`/api/rooms/${roomToMove.id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            room_id: roomToMove.room_id,
                            name: roomToMove.name,
                            description: roomToMove.description,
                            area_id: roomToMove.area_id,
                            x: newX,
                            y: newY,
                            z: newZ,
                            exits: roomToMove.exits || {}
                        })
                    });
                } catch (error) {
                    console.error(`Error updating room ${roomToMove.room_id}:`, error);
                }
            }
        }
    }
    draggedNodes.forEach(({ node }) => {
        node.style.cursor = 'grab';
        node.style.opacity = '1';
        node.style.zIndex = '';
    });
    isDraggingRoom = false;
    draggedRoom = null;
    draggedNode = null;
    draggedRooms = [];
    draggedNodes = [];
    if (typeof loadRooms === 'function') await loadRooms();
    renderMap();
// End of handleRoomDrop
}

// Handle selection start
export function handleSelectionStart(event) {
    if (isDraggingRoom) return;
    if (event.target.classList.contains('room-node')) return;
    if (!event.shiftKey) {
        clearMultiSelection();
    }
    isSelecting = true;
    const rect = event.currentTarget.getBoundingClientRect();
    selectionStart = {
        x: event.clientX - rect.left + event.currentTarget.scrollLeft,
        y: event.clientY - rect.top + event.currentTarget.scrollTop
    };
    if (!selectionBox) {
        selectionBox = document.createElement('div');
        selectionBox.className = 'selection-box';
        event.currentTarget.appendChild(selectionBox);
    }
    selectionBox.style.left = selectionStart.x + 'px';
    selectionBox.style.top = selectionStart.y + 'px';
    selectionBox.style.width = '0px';
    selectionBox.style.height = '0px';
    selectionBox.style.display = 'block';
// End of handleSelectionStart
}

// Handle canvas drag (selection or room move)
export function handleCanvasDrag(event) {
    if (isDraggingRoom && draggedNode) {
        const rect = event.currentTarget.getBoundingClientRect();
        const mouseX = event.clientX - rect.left + event.currentTarget.scrollLeft;
        const mouseY = event.clientY - rect.top + event.currentTarget.scrollTop;
        const newLeft = mouseX - dragOffset.x;
        const newTop = mouseY - dragOffset.y;
        const deltaX = newLeft - (draggedRoom.x * GRID_SIZE + CANVAS_CENTER + 10);
        const deltaY = newTop - (-draggedRoom.y * GRID_SIZE + CANVAS_CENTER + 10);
        draggedNodes.forEach(({ node, room }) => {
            const baseLeft = room.x * GRID_SIZE + CANVAS_CENTER + 10;
            const baseTop = -room.y * GRID_SIZE + CANVAS_CENTER + 10;
            node.style.left = (baseLeft + deltaX) + 'px';
            node.style.top = (baseTop + deltaY) + 'px';
            node.style.opacity = '0.6';
            node.style.zIndex = '1000';
        });
    } else if (isSelecting && selectionBox) {
        const rect = event.currentTarget.getBoundingClientRect();
        const currentX = event.clientX - rect.left + event.currentTarget.scrollLeft;
        const currentY = event.clientY - rect.top + event.currentTarget.scrollTop;
        const width = Math.abs(currentX - selectionStart.x);
        const height = Math.abs(currentY - selectionStart.y);
        const left = Math.min(currentX, selectionStart.x);
        const top = Math.min(currentY, selectionStart.y);
        selectionBox.style.left = left + 'px';
        selectionBox.style.top = top + 'px';
        selectionBox.style.width = width + 'px';
        selectionBox.style.height = height + 'px';
    }
// End of handleCanvasDrag
}

// Handle canvas mouse up (selection or room drop)
export function handleCanvasMouseUp(event) {
    if (isDraggingRoom) {
        handleRoomDrop(event);
    } else {
        handleSelectionEnd(event);
    }
// End of handleCanvasMouseUp
}

// Handle selection end
export function handleSelectionEnd(event) {
    if (!isSelecting) return;
    isSelecting = false;
    if (selectionBox) {
        const width = parseFloat(selectionBox.style.width);
        const height = parseFloat(selectionBox.style.height);
        if (width > 5 || height > 5) {
            window.justFinishedDrag = true;
            const boxRect = {
                left: parseFloat(selectionBox.style.left),
                top: parseFloat(selectionBox.style.top),
                right: parseFloat(selectionBox.style.left) + width,
                bottom: parseFloat(selectionBox.style.top) + height
            };
            const zFilter = document.getElementById('zLevelFilter').value;
            const filteredRooms = zFilter === 'all' 
                ? rooms 
                : rooms.filter(r => (r.z || 0) === parseInt(zFilter));
            filteredRooms.forEach(room => {
                const roomLeft = room.x * GRID_SIZE + CANVAS_CENTER + 10;
                const roomTop = -room.y * GRID_SIZE + CANVAS_CENTER + 10;
                const roomRight = roomLeft + 40;
                const roomBottom = roomTop + 40;
                if (roomLeft < boxRect.right && roomRight > boxRect.left &&
                    roomTop < boxRect.bottom && roomBottom > boxRect.top) {
                    if (!multiSelectedRooms.includes(room.id)) {
                        multiSelectedRooms.push(room.id);
                    }
                }
            });
            updateMultiSelection();
        }
        if(selectionBox != null) {
            selectionBox.style.display = 'none';
        }
    }
// End of handleSelectionEnd
}

// Update visual selection
export function updateMultiSelection() {
    renderMap();
    const copyBtn = document.getElementById('copySelectedBtn');
    const autoExitBtn = document.getElementById('autoExitBtn');
    if (multiSelectedRooms.length > 0) {
        copyBtn.style.display = 'inline-block';
        autoExitBtn.disabled = false;
    } else {
        copyBtn.style.display = 'none';
        autoExitBtn.disabled = true;
    }
    updateSelectionDisplay();
    if (typeof updateAutoRoomToggle === 'function') updateAutoRoomToggle();
// End of updateMultiSelection
}

// Clear multi selection
export function clearMultiSelection() {
    multiSelectedRooms = [];
    selectedRoom = null;
    updateMultiSelection();
// End of clearMultiSelection
}

// Coordinate display
export function updateCoordDisplay(event) {
    const coordDisplay = document.getElementById('coord-display');
    if (!coordDisplay) return;
    const canvas = document.getElementById('map-canvas');
    const rect = canvas.getBoundingClientRect();
    const scrollLeft = canvas.scrollLeft || 0;
    const scrollTop = canvas.scrollTop || 0;
    const clickX = event.clientX - rect.left + scrollLeft;
    const clickY = event.clientY - rect.top + scrollTop;
    const gridX = Math.round((clickX - (CANVAS_CENTER + 10)) / GRID_SIZE);
    const gridY = Math.round(-(clickY - (CANVAS_CENTER + 10)) / GRID_SIZE);
    const zFilter = document.getElementById('zLevelFilter').value;
    const gridZ = (zFilter === 'all') ? 0 : parseInt(zFilter);
    let displayText = `X: ${gridX}, Y: ${gridY}, Z: ${gridZ}`;
    if (multiSelectedRooms.length > 1) {
        displayText += ` | ${multiSelectedRooms.length} Rooms Selected`;
    } else if (multiSelectedRooms.length === 1) {
        const room = rooms.find(r => r.id === multiSelectedRooms[0]);
        if (room) {
            displayText += ` | Selected: ${room.name} (X: ${room.x}, Y: ${room.y}, Z: ${room.z})`;
        }
    } else if (selectedRoom) {
        displayText += ` | Selected: ${selectedRoom.name} (X: ${selectedRoom.x}, Y: ${selectedRoom.y}, Z: ${selectedRoom.z})`;
    }
    coordDisplay.textContent = displayText;
// End of updateCoordDisplay
}
