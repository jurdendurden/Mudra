// Setter for selectionBox to allow mutation from other modules
export function setSelectionBox(val) {
    selectionBox = val;
}
// Setters for other global variables
export function setRooms(val) { rooms = val; }
export function setAreas(val) { areas = val; }
export function setSelectedRoom(val) { selectedRoom = val; }
export function setRoomModal(val) { roomModal = val; }
export function setTooltip(val) { tooltip = val; }
export function setMultiSelectedRooms(val) { multiSelectedRooms = val; }
export function setIsSelecting(val) { isSelecting = val; }
export function setSelectionStart(val) { selectionStart = val; }
export function setJustFinishedDrag(val) { justFinishedDrag = val; }
export function setIsDraggingRoom(val) { isDraggingRoom = val; }
export function setDraggedRoom(val) { draggedRoom = val; }
export function setDraggedNode(val) { draggedNode = val; }
export function setDraggedRooms(val) { draggedRooms = val; }
export function setDraggedNodes(val) { draggedNodes = val; }
export function setDragOffset(val) { dragOffset = val; }
export function setUndoHistory(val) { undoHistory = val; }
export function setAutoRoomMode(val) { autoRoomMode = val; }
export function setAPIBase(val) { API_BASE = val; }
// map_builder_core.js
// Initialization, global state, API base setup, main entry point

// Global state variables
export let rooms = [];
export let areas = [];
export let selectedRoom = null;
export let roomModal = null;
export let tooltip = null;
export let multiSelectedRooms = [];
export let isSelecting = false;
export let selectionStart = { x: 0, y: 0 };
export let selectionBox = null;
export let justFinishedDrag = false;
export let isDraggingRoom = false;
export let draggedRoom = null;
export let draggedNode = null;
export let draggedRooms = [];
export let draggedNodes = [];
export let dragOffset = { x: 0, y: 0 };

// Canvas constants
export const CANVAS_PADDING = 10;
export const CANVAS_CENTER = 1000;
export const GRID_SIZE = 50;

// Undo history
export let undoHistory = [];
export const MAX_UNDO_STEPS = 3;

// Auto Room mode
export let autoRoomMode = true;

// API base (set by template)
export let API_BASE = '';

// Main entry point
export function initializeMapBuilder(apiBase) {
    API_BASE = apiBase || '';
    // Modal initialization (Bootstrap)
    roomModal = new window.bootstrap.Modal(document.getElementById('roomModal'));
    // Any other global setup can go here
}
