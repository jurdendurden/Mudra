// map_builder.js
// Entry point: imports all modules, initializes app
import { initializeMapBuilder, setRoomModal, roomModal, setDoorModal, doorModal, setSelectedRoom } from './map_builder_core.js';
const apiBase = window.API_BASE || '';
    
initializeMapBuilder(apiBase);
import { fetchAreas, fetchRooms } from './map_builder_api.js';
import { renderAreaList, renderRoomList, renderMap, filterRoomsByArea, toggleCoordinateLabels, toggleGridlines, updateGridAlignment } from './map_builder_render.js';
import { populateAreaSelect, saveRoom, deleteRoom, saveMap, showDoorHelp, editDoor, updateLockDifficultyLabel, updateDoorButtons, saveDoor, deleteDoor, selectAllExits, clearAllExits, autoSelectExits } from './map_builder_room_editor.js';
import { handleRoomDragStart, handleRoomDrop, handleSelectionStart, handleCanvasDrag, handleCanvasMouseUp, handleSelectionEnd, 
    updateMultiSelection, clearMultiSelection, updateCoordDisplay, toggleAutoRoom
     } from './map_builder_canvas.js';
import { addToUndoHistory, undoLastAction, updateUndoButton } from './map_builder_undo.js';
import { handleContextMenu, hideContextMenu, handleKeyPress, copySelectedRooms, deleteSelectedRooms, autoExitSelectedRooms, changeSelectedRoomNames } from './map_builder_context.js';
import { deepCopy, getNextRoomId, getOppositeDirection } from './map_builder_utils.js';
import { handleCanvasClick } from './map_builder_canvas.js';

// Main initialization logic
async function main() {
    // --- Ensure all required GUI elements exist (for minimal HTML) ---
    function ensureElement(parent, tag, attrs = {}, html = '') {
        let el = parent.querySelector(attrs.id ? `#${attrs.id}` : tag);
        if (!el) {
            el = document.createElement(tag);
            for (const [k, v] of Object.entries(attrs)) {
                el.setAttribute(k, v);
            }
            if (html) el.innerHTML = html;
            parent.appendChild(el);
        }
        return el;
    }
    window.renderMap = renderMap;
    window.toggleAutoRoom = toggleAutoRoom;
    window.toggleCoordinateLabels = toggleCoordinateLabels;
    window.toggleGridlines = toggleGridlines;
    window.updateGridAlignment = updateGridAlignment;
    window.copySelectedRooms = copySelectedRooms;
    window.autoExitSelectedRooms = autoExitSelectedRooms;
    window.undoLastAction = undoLastAction;
    window.saveMap = saveMap;
    window.saveRoom = saveRoom;
    window.deleteRoom = deleteRoom;
    window.selectAllExits = selectAllExits;
    window.clearAllExits = clearAllExits;
    window.autoSelectExits = autoSelectExits;
    window.showDoorHelp = showDoorHelp;
    window.editDoor = editDoor;
    window.saveDoor = saveDoor;
    window.deleteDoor = deleteDoor;
    window.changeSelectedRoomNames = changeSelectedRoomNames;
    // Main container
    let builderContainer = document.querySelector('.builder-container');
    if (!builderContainer) {
        builderContainer = document.createElement('div');
        builderContainer.className = 'builder-container';
        document.body.prepend(builderContainer);
    }
    // Header
    let builderHeader = builderContainer.querySelector('.builder-header');
    if (!builderHeader) {
        builderHeader = document.createElement('div');
        
        builderHeader.className = 'builder-header';
        builderHeader.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <h3><i class="fas fa-hammer"></i> Mudra Map Builder</h3>
                <div class="d-flex align-items-center" id="toolbar-controls"></div>
            </div>
        `;
        builderContainer.appendChild(builderHeader);
    }
            
    // --- Modal Creation Functions ---
    function createRoomModal() {
        let modalDiv = document.getElementById('roomModal');
        setRoomModal(new bootstrap.Modal(modalDiv));
    }

    function createDoorModal() {
        let modalDiv = document.getElementById('doorModal');
        setDoorModal(new bootstrap.Modal(modalDiv));
    }

    // Create modals
    createRoomModal();
    createDoorModal();
    
    toggleGridlines();
    // Get API base from template variable
    

    // Load initial data
    try {
        const areaData = await fetchAreas();
        const roomData = await fetchRooms();
        // Assign to global state (imported from core)
        import('./map_builder_core.js').then(core => {
            core.areas.length = 0;
            core.areas.push(...areaData);
            core.rooms.length = 0;
            core.rooms.push(...roomData);

            renderAreaList();
            filterRoomsByArea();        
            populateAreaSelect();
        });
        
    } catch (error) {
        console.error('Error loading initial data:', error);
    }

    // Attach event listeners
    const canvas = document.getElementById('map-canvas');
    
    if (canvas) {
        canvas.addEventListener('mousedown', handleSelectionStart);
        canvas.addEventListener('mousemove', handleCanvasDrag);
        canvas.addEventListener('mouseup', handleCanvasMouseUp);
        canvas.addEventListener('mouseleave', handleSelectionEnd);
        canvas.addEventListener('click', handleCanvasClick);
    }
    document.addEventListener('keydown', handleKeyPress);
    // ...other event listeners as needed...
}

if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', main);
} else {
    main();
}
