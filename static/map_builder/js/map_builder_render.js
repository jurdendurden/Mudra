// map_builder_render.js
// Rendering: map, sidebar, tooltips, gridlines, coordinate labels
import { rooms, areas, selectedRoom, multiSelectedRooms, CANVAS_CENTER, GRID_SIZE, selectionBox, setSelectionBox } from './map_builder_core.js';

// Render area list in sidebar
export function renderAreaList() {
    const select = document.getElementById('area-filter');
    select.innerHTML = '';
    areas.forEach(area => {
        const option = document.createElement('option');
        option.value = area.area_id;
        option.textContent = area.name;
        select.appendChild(option);
    });
    // Select the first area by default
    if (areas.length > 0) {
        select.value = areas[0].area_id;
    }
    // Add change event listener to filter rooms
    select.addEventListener('change', filterRoomsByArea);
}

function filterRoomsByArea() {
    const selectedAreaId = document.getElementById('area-filter').value;
    clearMultiSelection();
    renderRoomList(selectedAreaId);
    renderMap();
}

// Render room list in sidebar
export function renderRoomList(filterAreaId = null) {
    const select = document.getElementById('room-list');
    select.innerHTML = '<option value="">Select a room...</option>';
    // Filter rooms by area if specified
    const filteredRooms = !filterAreaId 
        ? rooms 
        : rooms.filter(room => {
            const area = areas.find(a => a.id === room.area_id);
            return area && area.area_id === filterAreaId;
        });
    // Sort rooms by room_id
    filteredRooms.sort((a, b) => a.room_id.localeCompare(b.room_id));
    filteredRooms.forEach(room => {
        const option = document.createElement('option');
        option.value = room.id;
        option.textContent = `${room.room_id} - ${room.name} (${room.x}, ${room.y}, ${room.z || 0})`;
        select.appendChild(option);
    });
    // Add change handler to select room on canvas
    select.onchange = function() {
        if (this.value) {
            const selectedOptions = Array.from(this.selectedOptions);
            const selectedRoomIds = selectedOptions.map(option => parseInt(option.value));
            multiSelectedRooms = selectedRoomIds;
            selectedRoom = rooms.find(r => r.id === selectedRoomIds[0]) || null;
            displayClearSelectedRooms();
            selectRoomsByIds(selectedRoomIds);
        } else {
            multiSelectedRooms = [];
            selectedRoom = null;
            displayClearSelectedRooms();
            selectRoomsByIds([]);
        }
    };
// End of renderRoomList
}

// Render map canvas
export function renderMap() {
    const canvas = document.getElementById('map-canvas');
    canvas.innerHTML = '';
    setSelectionBox(null);
    const zFilter = document.getElementById('zLevelFilter').value;
    const areaFilter = document.getElementById('area-filter')?.value || null;
    const showSurrounding = document.getElementById('surroundingAreasToggle')?.checked || false;
    // Populate Z-level filter if empty
    const zLevels = [...new Set(rooms.map(r => r.z || 0))].sort((a, b) => a - b);
    const zLevelSelect = document.getElementById('zLevelFilter');
    const currentValue = zLevelSelect.value;
    zLevelSelect.innerHTML = '<option value="all">All</option>';
    zLevels.forEach(z => {
        const option = document.createElement('option');
        option.value = z;
        option.textContent = z;
        zLevelSelect.appendChild(option);
    });
    zLevelSelect.value = currentValue;
    // Filter rooms by Z-level and area
    let filteredRooms = rooms;
    if (zFilter !== 'all') {
        filteredRooms = filteredRooms.filter(r => (r.z || 0) === parseInt(zFilter));
    }
    if (areaFilter) {
        filteredRooms = filteredRooms.filter(room => {
            const area = areas.find(a => a.id === room.area_id);
            return area && area.area_id === areaFilter;
        });
    }
    // Get surrounding area rooms if toggle is on
    let surroundingRooms = [];
    if (showSurrounding && filteredRooms.length > 0) {
        surroundingRooms = rooms.filter(room => {
            if (filteredRooms.some(fr => fr.id === room.id)) return false;
            if (zFilter !== 'all' && (room.z || 0) !== parseInt(zFilter)) return false;
            return filteredRooms.some(fr => {
                const distance = Math.sqrt(
                    Math.pow(room.x - fr.x, 2) + 
                    Math.pow(room.y - fr.y, 2) + 
                    Math.pow((room.z || 0) - (fr.z || 0), 2)
                );
                return distance <= 30;
            });
        });
    }
    // Render room nodes
    filteredRooms.forEach(room => {
        const node = document.createElement('div');
        node.className = 'room-node';
        node.style.left = (room.x * GRID_SIZE + CANVAS_CENTER + 10) + 'px';
        node.style.top = (-room.y * GRID_SIZE + CANVAS_CENTER + 10) + 'px';
        node.innerHTML = `${room.name}`;
        if (room.exits) {
            if (room.exits.up) {
                const upArrow = document.createElement('div');
                upArrow.className = 'exit-indicator exit-up';
                node.appendChild(upArrow);
            }
            if (room.exits.down) {
                const downArrow = document.createElement('div');
                downArrow.className = 'exit-indicator exit-down';
                node.appendChild(downArrow);
            }
        }
        if (selectedRoom && selectedRoom.id === room.id) {
            node.classList.add('selected');
        }
        if (multiSelectedRooms.includes(room.id)) {
            node.classList.add('multi-selected');
        }
        node.addEventListener('mouseenter', (e) => showTooltip(e, room));
        node.addEventListener('mouseleave', hideTooltip);
        node.addEventListener('mousemove', updateTooltipPosition);
        node.onclick = (e) => {
            e.stopPropagation();
            if (e.ctrlKey) {
                const roomIndex = multiSelectedRooms.indexOf(room.id);
                if (roomIndex > -1) {
                    multiSelectedRooms.splice(roomIndex, 1);
                    if (selectedRoom && selectedRoom.id === room.id) {
                        selectedRoom = multiSelectedRooms.length > 0 
                            ? rooms.find(r => r.id === multiSelectedRooms[0]) 
                            : null;
                    }
                } else {
                    multiSelectedRooms.push(room.id);
                    selectedRoom = room;
                }
                updateMultiSelection();
            } else if (e.shiftKey) {
                if (!multiSelectedRooms.includes(room.id)) {
                    multiSelectedRooms.push(room.id);
                }
                selectedRoom = room;
                updateMultiSelection();
            } else {
                multiSelectedRooms = [];
                selectRoomVisual(room, node);
            }
        };
        node.ondblclick = (e) => {
            if (!e.ctrlKey && !e.shiftKey) {
                openRoomEditor(room);
            }
        };
        canvas.appendChild(node);
    });
    surroundingRooms.forEach(room => {
        const node = document.createElement('div');
        node.className = 'room-node surrounding-area';
        node.style.left = (room.x * GRID_SIZE + CANVAS_CENTER + 10) + 'px';
        node.style.top = (-room.y * GRID_SIZE + CANVAS_CENTER + 10) + 'px';
        node.innerHTML = `${room.name}`;
        if (room.exits) {
            if (room.exits.up) {
                const upArrow = document.createElement('div');
                upArrow.className = 'exit-indicator exit-up';
                node.appendChild(upArrow);
            }
            if (room.exits.down) {
                const downArrow = document.createElement('div');
                downArrow.className = 'exit-indicator exit-down';
                node.appendChild(downArrow);
            }
        }
        node.addEventListener('mouseenter', (e) => showTooltip(e, room));
        node.addEventListener('mouseleave', hideTooltip);
        node.addEventListener('mousemove', updateTooltipPosition);
        canvas.appendChild(node);
    });
    filteredRooms.forEach(room => {
        if (room.exits) {
            Object.entries(room.exits).forEach(([direction, targetRoomId]) => {
                if (direction === 'up' || direction === 'down') return;
                const targetRoom = rooms.find(r => r.room_id === targetRoomId);
                if (targetRoom && filteredRooms.some(fr => fr.id === targetRoom.id)) {
                    drawConnection(room, targetRoom, direction);
                }
            });
        }
    });
    const showCoordinatesToggle = document.getElementById('showCoordinatesToggle');
    if (showCoordinatesToggle && showCoordinatesToggle.checked) {
        toggleCoordinateLabels();
    }
// End of renderMap
}

// Tooltip rendering
export function showTooltip(event, room) {
    let tooltip = document.getElementById('room-tooltip');
    if (!tooltip) {
        tooltip = document.createElement('div');
        tooltip.className = 'room-tooltip';
        tooltip.id = 'room-tooltip';
        document.body.appendChild(tooltip);
    }
    let tooltipText = `Coords: (${room.x}, ${room.y}, ${room.z || 0})\nRoom ID: ${room.room_id}`;
    if (room.area_id) {
        const area = areas.find(a => a.id === room.area_id);
        if (area) {
            tooltipText += `\nArea: ${area.name}`;
        }
    }
    if (room.exits && Object.keys(room.exits).length > 0) {
        tooltipText += '\n\nExits:';
        Object.entries(room.exits).forEach(([direction, targetRoomId]) => {
            const targetRoom = rooms.find(r => r.room_id === targetRoomId);
            const targetName = targetRoom ? targetRoom.name : 'Unknown';
            tooltipText += `\n  ${direction} → ${targetRoomId} (${targetName})`;
        });
    } else {
        tooltipText += '\n\nExits: None';
    }
    tooltip.textContent = tooltipText;
    tooltip.style.left = event.pageX + 15 + 'px';
    tooltip.style.top = event.pageY + 15 + 'px';
    setTimeout(() => {
        tooltip.classList.add('show');
    }, 10);
// End of showTooltip
}

export function hideTooltip() {
    const tooltip = document.getElementById('room-tooltip');
    if (tooltip) {
        tooltip.classList.remove('show');
    }
// End of hideTooltip
}

export function updateTooltipPosition(event) {
    const tooltip = document.getElementById('room-tooltip');
    if (tooltip) {
        tooltip.style.left = event.pageX + 15 + 'px';
        tooltip.style.top = event.pageY + 15 + 'px';
    }
// End of updateTooltipPosition
}

// Gridlines and coordinate labels
export function toggleGridlines() {
    const canvas = document.getElementById('map-canvas');
    const toggle = document.getElementById('gridlinesToggle');
    const alignment = document.getElementById('gridAlignmentSelect').value;
    canvas.classList.remove('gridlines-boxed', 'gridlines-centered');
    if (toggle.checked) {
        if (alignment === 'centered') {
            canvas.classList.add('gridlines-centered');
        } else {
            canvas.classList.add('gridlines-boxed');
        }
    }
// End of toggleGridlines
}

export function toggleCoordinateLabels() {
    const canvas = document.getElementById('map-canvas');
    const toggle = document.getElementById('showCoordinatesToggle');
    const existingLabels = canvas.querySelectorAll('.coordinate-label');
    existingLabels.forEach(label => label.remove());
    if (toggle.checked) {
        const minCoord = -20;
        const maxCoord = 20;
        for (let x = minCoord; x <= maxCoord; x++) {
            if (x === 0) continue;
            const label = document.createElement('div');
            label.className = 'coordinate-label x-axis';
            label.textContent = x;
            label.style.left = `${x * GRID_SIZE + CANVAS_CENTER + 10}px`;
            label.style.top = '2px';
            canvas.appendChild(label);
        }
        for (let y = minCoord; y <= maxCoord; y++) {
            if (y === 0) continue;
            const label = document.createElement('div');
            label.className = 'coordinate-label y-axis';
            label.textContent = y;
            label.style.left = '2px';
            label.style.top = `${-y * GRID_SIZE + CANVAS_CENTER + 10}px`;
            canvas.appendChild(label);
        }
        const originLabel = document.createElement('div');
        originLabel.className = 'coordinate-label';
        originLabel.textContent = '0';
        originLabel.style.left = '0px';
        originLabel.style.top = '0px';
        originLabel.style.color = '#3498db';
        canvas.appendChild(originLabel);
    }
// End of toggleCoordinateLabels
}

export function updateGridAlignment() {
    const toggle = document.getElementById('gridlinesToggle');
    if (toggle.checked) {
        toggleGridlines();
    }
}
// End of updateGridAlignment
// Draw connection between rooms (horizontal connections only - up/down use arrows)
function drawConnection(room1, room2, direction) {
    const canvas = document.getElementById('map-canvas');
    const line = document.createElement('div');
    line.className = 'connection-line';
    const x1 = room1.x * GRID_SIZE + CANVAS_CENTER + 10 + (GRID_SIZE / 2 - 5);
    const y1 = -room1.y * GRID_SIZE + CANVAS_CENTER + 10 + (GRID_SIZE / 2 - 5);
    const x2 = room2.x * GRID_SIZE + CANVAS_CENTER + 10 + (GRID_SIZE / 2 - 5);
    const y2 = -room2.y * GRID_SIZE + CANVAS_CENTER + 10 + (GRID_SIZE / 2 - 5);
    const angle = Math.atan2(y2 - y1, x2 - x1);
    const angleDeg = angle * 180 / Math.PI;
    const fullLength = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
    const lineOffset = 15;
    const length = Math.max(fullLength - (lineOffset * 2), 2);
    const startX = x1 + Math.cos(angle) * lineOffset;
    const startY = y1 + Math.sin(angle) * lineOffset;
    line.style.left = startX + 'px';
    line.style.top = startY + 'px';
    line.style.width = length + 'px';
    line.style.transform = `rotate(${angleDeg}deg)`;
    canvas.appendChild(line);
}
// Utility functions for selection display
function displayClearSelectedRooms() {
    document.querySelectorAll('.room-node').forEach(n => {
        n.classList.remove('selected');
        n.classList.remove('multi-selected');
    });
}

function selectRoomsByIds(roomIds) {
    displayClearSelectedRooms();
    roomIds.forEach(id => {
        selectRoomById(id, false);
    });
}

function selectRoomById(roomId, remove = true) {
    const room = rooms.find(r => r.id === roomId);
    if (!room) return;
    selectedRoom = room;
    if(remove) {
        displayClearSelectedRooms();
    }
    const nodes = document.querySelectorAll('.room-node');
    nodes.forEach(node => {
        if (node.innerHTML.includes(room.name) && 
            node.style.left === `${room.x * GRID_SIZE + CANVAS_CENTER + 10}px` &&
            node.style.top === `${-room.y * GRID_SIZE + CANVAS_CENTER + 10}px`) {
            node.classList.add('selected');
            if(!multiSelectedRooms.includes(room.id)) {
                multiSelectedRooms.push(room.id);
            }
            node.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
        }
    });
    updateSelectionDisplay();
    updateAutoRoomToggle();
}

function selectRoomVisual(room, node) {
    selectedRoom = room;
    displayClearSelectedRooms();
    node.classList.add('selected');
    updateSelectionDisplay();
    updateAutoRoomToggle();
}

export function updateMultiSelection() {
    document.querySelectorAll('.room-node').forEach(n => {
        n.classList.remove('selected');
        n.classList.remove('multi-selected');
    });
    multiSelectedRooms.forEach(id => {
        const room = rooms.find(r => r.id === id);
        if (room) {
            const nodes = document.querySelectorAll('.room-node');
            nodes.forEach(node => {
                if (node.innerHTML.includes(room.name) && 
                    node.style.left === `${room.x * GRID_SIZE + CANVAS_CENTER + 10}px` &&
                    node.style.top === `${-room.y * GRID_SIZE + CANVAS_CENTER + 10}px`) {
                    node.classList.add('multi-selected');
                }
            });
        }
    });
    updateSelectionDisplay();
    updateAutoRoomToggle();
}

export function updateSelectionDisplay() {
    const coordDisplay = document.getElementById('coord-display');
    if (!coordDisplay) return;
    const currentText = coordDisplay.textContent;
    const coordMatch = currentText.match(/X: (-?\d+), Y: (-?\d+), Z: (-?\d+)/);
    let displayText = coordMatch ? coordMatch[0] : 'X: 0, Y: 0, Z: 0';
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
    const roomList = document.getElementById('room-list');
    if (roomList) {
        for (let i = 0; i < roomList.options.length; i++) {
            roomList.options[i].classList.remove('selected');
            roomList.options[i].selected = false;
        }
        if (multiSelectedRooms.length > 0) {
            for (let i = 0; i < roomList.options.length; i++) {
                if (multiSelectedRooms.includes(Number.parseInt(roomList.options[i].value))) {
                    roomList.options[i].selected = true;
                    roomList.options[i].classList.add('selected');
                }
            }
        } else if (selectedRoom) {
            for (let i = 0; i < roomList.options.length; i++) {
                if (roomList.options[i].value == selectedRoom.id) {
                    roomList.options[i].selected = true;
                    roomList.options[i].classList.add('selected');
                    break;
                }
            }
        } else {
            if (roomList.options.length > 0) {
                roomList.options[0].selected = true;
            }
        }
    }
}

// Update auto room toggle based on selection
export function updateAutoRoomToggle() {
    const toggle = document.getElementById('autoRoomToggle');
    const label = document.getElementById('autoRoomLabel');
    const canEnable = selectedRoom && multiSelectedRooms.length <= 1;
    toggle.disabled = !canEnable;
    label.style.opacity = canEnable ? '1' : '0.5';
    if (!canEnable && window.autoRoomMode) {
        toggle.checked = false;
        window.autoRoomMode = false;
    }
}

export function clearMultiSelection() {
    multiSelectedRooms = [];
    displayClearSelectedRooms();
    updateSelectionDisplay();
    updateAutoRoomToggle();
}