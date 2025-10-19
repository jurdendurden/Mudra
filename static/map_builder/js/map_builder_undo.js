// map_builder_undo.js
// Undo/redo stack, action history, undo button state
import { undoHistory, MAX_UNDO_STEPS, setUndoHistory } from './map_builder_core.js';

// Add action to undo history
export function addToUndoHistory(action) {
    let newHistory = undoHistory.slice();
    if (newHistory.length >= MAX_UNDO_STEPS) {
        newHistory.shift();
    }
    newHistory.push(action);
    setUndoHistory(newHistory);
}

// Undo last action
export function undoLastAction() {
    // ...undo logic, revert last action...
}

// Update undo button state
export function updateUndoButton() {
    // ...enable/disable undo button based on history...
}
