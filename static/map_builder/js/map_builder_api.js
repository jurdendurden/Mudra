// map_builder_api.js
// API communication: load/save rooms/areas, fetch wrappers
import { API_BASE } from './map_builder_core.js';

export async function fetchAreas() {
    const response = await fetch(`${API_BASE}/api/areas`);
    if (!response.ok) throw new Error('Failed to fetch areas');
    return await response.json();
}

export async function fetchRooms() {
    const response = await fetch(`${API_BASE}/api/rooms`);
    if (!response.ok) throw new Error('Failed to fetch rooms');
    return await response.json();
}

export async function createRoom(roomData) {
    const response = await fetch(`${API_BASE}/api/rooms`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(roomData)
    });
    if (!response.ok) throw new Error('Failed to create room');
    return await response.json();
}

export async function updateRoom(roomId, roomData) {
    const response = await fetch(`${API_BASE}/api/rooms/${roomId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(roomData)
    });
    if (!response.ok) throw new Error('Failed to update room');
    return await response.json();
}

export async function deleteRoom(roomId) {
    const response = await fetch(`${API_BASE}/api/rooms/${roomId}`, {
        method: 'DELETE'
    });
    if (!response.ok) throw new Error('Failed to delete room');
    return await response.json();
}

export async function createArea(areaData) {
    const response = await fetch(`${API_BASE}/api/areas`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(areaData)
    });
    if (!response.ok) throw new Error('Failed to create area');
    return await response.json();
}
