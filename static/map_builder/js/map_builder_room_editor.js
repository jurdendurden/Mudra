// map_builder_room_editor.js
// Room/area modal logic, exit management, dropdown population
import { areas, rooms, selectedRoom, roomModal } from './map_builder_core.js';
import { createRoom, updateRoom, deleteRoom, createArea } from './map_builder_api.js';
import { renderMap, renderAreaList, renderRoomList } from './map_builder_render.js';

// Populate area select dropdown in room modal
export function populateAreaSelect() {
    const select = document.getElementById('areaSelect');
    select.innerHTML = '<option value="">Select Area</option>';
    areas.forEach(area => {
        const option = document.createElement('option');
        option.value = area.area_id;
        option.textContent = area.name;
        select.appendChild(option);
    });
}

// Open room editor modal
export function openRoomEditor(room) {
    selectedRoom = room;
    // ...populate modal fields with room data...
    roomModal.show();
}

// Save room (create or update)
export async function saveRoom(roomData) {
    if (roomData.id) {
        await updateRoom(roomData.id, roomData);
    } else {
        await createRoom(roomData);
    }
    // ...refresh rooms and UI...
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
