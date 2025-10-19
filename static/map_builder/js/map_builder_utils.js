// map_builder_utils.js
// Helper functions, shared constants

// Deep copy utility
export function deepCopy(obj) {
    return JSON.parse(JSON.stringify(obj));
}

// Coordinate math utilities
// Generate the next available room ID in the format 'room_XXX'
export function getNextRoomId() {
    // Assume global 'rooms' array is available via import in modules
    if (typeof window !== 'undefined' && window.rooms && window.rooms.length > 0) {
        const roomNumbers = window.rooms
            .map(r => r.room_id)
            .filter(id => id && id.startsWith('room_'))
            .map(id => parseInt(id.replace('room_', '')))
            .filter(num => !isNaN(num))
            .sort((a, b) => a - b);
        if (roomNumbers.length === 0) {
            return 'room_001';
        }
        // Find first gap in sequence
        for (let i = 1; i <= roomNumbers[roomNumbers.length - 1]; i++) {
            if (!roomNumbers.includes(i)) {
                return `room_${String(i).padStart(3, '0')}`;
            }
        }
        // No gaps, increment max
        const nextNumber = roomNumbers[roomNumbers.length - 1] + 1;
        return `room_${String(nextNumber).padStart(3, '0')}`;
    }
    // Fallback if no rooms available
    return 'room_001';
}

// Return the opposite direction string for a given direction
export function getOppositeDirection(direction) {
    const opposites = {
        north: 'south',
        south: 'north',
        east: 'west',
        west: 'east',
        up: 'down',
        down: 'up',
        northeast: 'southwest',
        northwest: 'southeast',
        southeast: 'northwest',
        southwest: 'northeast'
    };
    return opposites[direction] || null;
}

// Other shared constants or helpers can be added here
