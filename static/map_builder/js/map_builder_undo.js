// map_builder_undo.js
// Undo/redo stack, action history, undo button state
import { undoHistory, MAX_UNDO_STEPS } from './map_builder_core.js';

// Add action to undo history
export function addToUndoHistory(action) {
    if (undoHistory.length >= MAX_UNDO_STEPS) {
        undoHistory.shift();
    }
    undoHistory.push(action);
}

// Undo last action
export function undoLastAction() {
    // ...undo logic, revert last action...
}

// Update undo button state
export function updateUndoButton() {
    // ...enable/disable undo button based on history...
}
