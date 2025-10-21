// map_builder_undo.js
// Undo/redo stack, action history, undo button state
import { undoHistory, MAX_UNDO_STEPS, setUndoHistory, setRooms } from './map_builder_core.js';
import { fetchRooms, createRoom, deleteRoom, updateRoom } from './map_builder_api.js';
import { renderMap } from './map_builder_render.js';

// Add action to undo history
export function addToUndoHistory(action) {
    undoHistory.push(action);
    
    // Keep only last 3 actions
    if (undoHistory.length > MAX_UNDO_STEPS) {
        undoHistory.shift();
    }
    
    updateUndoButton();
}

// Update undo button state
export function updateUndoButton() {
    const undoBtn = document.getElementById('undoBtn');
    undoBtn.disabled = undoHistory.length === 0;
}

// Undo last action
export async function undoLastAction() {
    if (undoHistory.length === 0) {
        return;
    }
    
    const action = undoHistory.pop();
    updateUndoButton();
    
    try {
        switch (action.type) {
        case 'create':
            await deleteRoom(action.room.id);
            break;
            
        case 'delete':
            // Undo deletion by recreating the room
            await createRoom(action.room);
            break;
                    
        case 'update':
            // Undo update by restoring previous state
            await updateRoom(action.room.id, action.previousState);
            break;

        case 'bulk':
            // Undo bulk operation
            for (const subAction of action.actions.reverse()) {
                // Recursively undo each action in the bulk operation
                undoHistory.push(subAction);
                await undoLastAction();
            }
            break;
        }
                
        setRooms(await fetchRooms());
        renderMap();
        console.log('Undo successful');
    } catch (error) {
        console.error('Error undoing action:', error);
        alert('Error undoing action');
    }
}