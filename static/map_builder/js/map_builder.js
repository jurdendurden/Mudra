// map_builder.js
// Entry point: imports all modules, initializes app
import { initializeMapBuilder } from './map_builder_core.js';
import { fetchAreas, fetchRooms } from './map_builder_api.js';
import { renderAreaList, renderRoomList, renderMap, filterRoomsByArea } from './map_builder_render.js';
import { populateAreaSelect } from './map_builder_room_editor.js';
import { handleRoomDragStart, handleRoomDrop, handleSelectionStart, handleCanvasDrag, handleCanvasMouseUp, handleSelectionEnd, updateMultiSelection, clearMultiSelection, updateCoordDisplay } from './map_builder_canvas.js';
import { addToUndoHistory, undoLastAction, updateUndoButton } from './map_builder_undo.js';
import { handleContextMenu, hideContextMenu, handleKeyPress, copySelectedRooms, deleteSelectedRooms, autoExitSelectedRooms, changeSelectedRoomNames } from './map_builder_context.js';
import { deepCopy, getNextRoomId, getOppositeDirection } from './map_builder_utils.js';


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
    // Import needed functions
    const { renderMap, toggleGridlines, toggleCoordinateLabels, updateGridAlignment } = await import('./map_builder_render.js');
    const { toggleAutoRoom } = await import('./map_builder_canvas.js');

    // Toolbar controls (programmatic creation)
    let toolbar = builderHeader.querySelector('#toolbar-controls');
    if (toolbar) {
        // Helper to create a div with class and children
        function createDivWithChildren(className, children) {
            const div = document.createElement('div');
            div.className = className;
            children.forEach(child => div.appendChild(child));
            return div;
        }

        // Surrounding Areas toggle
        const surroundingAreasToggle = document.createElement('input');
        surroundingAreasToggle.className = 'form-check-input';
        surroundingAreasToggle.type = 'checkbox';
        surroundingAreasToggle.id = 'surroundingAreasToggle';
        const surroundingAreasLabel = document.createElement('label');
        surroundingAreasLabel.className = 'form-check-label text-white';
        surroundingAreasLabel.htmlFor = 'surroundingAreasToggle';
        surroundingAreasLabel.innerHTML = '<i class="fas fa-map-marked-alt"></i> Surrounding Areas';
        const surroundingAreasDiv = createDivWithChildren('form-check form-switch me-4', [surroundingAreasToggle, surroundingAreasLabel]);

        // Auto Room toggle
        const autoRoomToggle = document.createElement('input');
        autoRoomToggle.className = 'form-check-input';
        autoRoomToggle.type = 'checkbox';
        autoRoomToggle.id = 'autoRoomToggle';
        autoRoomToggle.disabled = true;
        const autoRoomLabel = document.createElement('label');
        autoRoomLabel.className = 'form-check-label text-white';
        autoRoomLabel.htmlFor = 'autoRoomToggle';
        autoRoomLabel.id = 'autoRoomLabel';
        autoRoomLabel.style.opacity = '0.5';
        autoRoomLabel.innerHTML = '<i class="fas fa-walking"></i> Auto Room';
        const autoRoomDiv = createDivWithChildren('form-check form-switch me-4', [autoRoomToggle, autoRoomLabel]);

        // Show Coordinates toggle
        const showCoordinatesToggle = document.createElement('input');
        showCoordinatesToggle.className = 'form-check-input';
        showCoordinatesToggle.type = 'checkbox';
        showCoordinatesToggle.id = 'showCoordinatesToggle';
        const showCoordinatesLabel = document.createElement('label');
        showCoordinatesLabel.className = 'form-check-label text-white';
        showCoordinatesLabel.htmlFor = 'showCoordinatesToggle';
        showCoordinatesLabel.innerHTML = '<i class="fas fa-hashtag"></i> Show X/Y';
        const showCoordinatesDiv = createDivWithChildren('form-check form-switch me-4', [showCoordinatesToggle, showCoordinatesLabel]);

        // Gridlines toggle
        const gridlinesToggle = document.createElement('input');
        gridlinesToggle.className = 'form-check-input';
        gridlinesToggle.type = 'checkbox';
        gridlinesToggle.id = 'gridlinesToggle';
        gridlinesToggle.checked = true;
        const gridlinesLabel = document.createElement('label');
        gridlinesLabel.className = 'form-check-label text-white';
        gridlinesLabel.htmlFor = 'gridlinesToggle';
        gridlinesLabel.innerHTML = '<i class="fas fa-border-all"></i> Gridlines';
        const gridlinesDiv = createDivWithChildren('form-check form-switch me-2', [gridlinesToggle, gridlinesLabel]);

        // Grid Alignment select
        const gridAlignmentSelect = document.createElement('select');
        gridAlignmentSelect.className = 'form-select form-select-sm me-4';
        gridAlignmentSelect.id = 'gridAlignmentSelect';
        gridAlignmentSelect.style.width = '140px';
        const boxedOption = document.createElement('option');
        boxedOption.value = 'boxed';
        boxedOption.textContent = 'Boxed';
        const centeredOption = document.createElement('option');
        centeredOption.value = 'centered';
        centeredOption.textContent = 'Centered';
        gridAlignmentSelect.appendChild(boxedOption);
        gridAlignmentSelect.appendChild(centeredOption);

        // Z-Level label and select
        const zLevelLabel = document.createElement('label');
        zLevelLabel.className = 'me-2 text-white';
        zLevelLabel.textContent = 'Z-Level:';
        const zLevelFilter = document.createElement('select');
        zLevelFilter.className = 'form-select me-3';
        zLevelFilter.id = 'zLevelFilter';
        zLevelFilter.style.width = '100px';
        const allOption = document.createElement('option');
        allOption.value = 'all';
        allOption.textContent = 'All';
        zLevelFilter.appendChild(allOption);

        // Copy Selected button
        const copySelectedBtn = document.createElement('button');
        copySelectedBtn.className = 'btn btn-info btn-sm me-2';
        copySelectedBtn.id = 'copySelectedBtn';
        copySelectedBtn.style.display = 'none';
        copySelectedBtn.innerHTML = '<i class="fas fa-copy"></i> Copy Selected';

        // Auto Exit button
        const autoExitBtn = document.createElement('button');
        autoExitBtn.className = 'btn btn-warning btn-sm me-2';
        autoExitBtn.id = 'autoExitBtn';
        autoExitBtn.disabled = true;
        autoExitBtn.innerHTML = '<i class="fas fa-route"></i> Auto Exit';

        // Undo button
        const undoBtn = document.createElement('button');
        undoBtn.className = 'btn btn-secondary btn-sm me-2';
        undoBtn.id = 'undoBtn';
        undoBtn.disabled = true;
        undoBtn.innerHTML = '<i class="fas fa-undo"></i> Undo';

        // Save Map button
        const saveMapBtn = document.createElement('button');
        saveMapBtn.className = 'btn btn-success me-2';
        saveMapBtn.id = 'saveMapBtn';
        saveMapBtn.innerHTML = '<i class="fas fa-save"></i> Save Map';

        // Clear toolbar and append all controls
        toolbar.innerHTML = '';
        toolbar.appendChild(surroundingAreasDiv);
        toolbar.appendChild(autoRoomDiv);
        toolbar.appendChild(showCoordinatesDiv);
        toolbar.appendChild(gridlinesDiv);
        toolbar.appendChild(gridAlignmentSelect);
        toolbar.appendChild(zLevelLabel);
        toolbar.appendChild(zLevelFilter);
        toolbar.appendChild(copySelectedBtn);
        toolbar.appendChild(autoExitBtn);
        toolbar.appendChild(undoBtn);
        toolbar.appendChild(saveMapBtn);

        // Attach event listeners
        surroundingAreasToggle.addEventListener('change', (e) => {
            e.preventDefault();
            renderMap();
        });
        autoRoomToggle.addEventListener('change', (e) => {
            e.preventDefault();
            toggleAutoRoom();
        });
        showCoordinatesToggle.addEventListener('change', (e) => {
            e.preventDefault();
            toggleCoordinateLabels();
        });
        gridlinesToggle.addEventListener('change',(e) => {
            e.preventDefault();
            toggleGridlines();
        });
        gridAlignmentSelect.addEventListener('change', (e) => {
            e.preventDefault();
            updateGridAlignment();
        });
        zLevelFilter.addEventListener('change', (e) => {
            e.preventDefault();
            renderMap();
        });
    }
    // (Other buttons can be hooked up here as needed)
    // Main content
    let builderMain = builderContainer.querySelector('.builder-main');
    if (!builderMain) {
        builderMain = document.createElement('div');
        builderMain.className = 'builder-main';
        builderContainer.appendChild(builderMain);
    }
    // Sidebar
    let sidebar = builderMain.querySelector('.sidebar');
    if (!sidebar) {
        sidebar = document.createElement('div');
        sidebar.className = 'sidebar';
        sidebar.innerHTML = `
            <h5>Current Area</h5>
            <select class="form-select mb-3" id="area-filter"></select>
            <h5>Rooms</h5>
            <select class="form-select" id="room-list" size="20" multiple></select>
        `;
        builderMain.appendChild(sidebar);
    }
    // Canvas container and map-canvas
    let canvasContainer = builderMain.querySelector('.canvas-container');
    if (!canvasContainer) {
        canvasContainer = document.createElement('div');
        canvasContainer.className = 'canvas-container';
        builderMain.appendChild(canvasContainer);
    }
    let mapCanvas = canvasContainer.querySelector('#map-canvas');
    if (!mapCanvas) {
        mapCanvas = document.createElement('div');
        mapCanvas.className = 'map-canvas';
        mapCanvas.id = 'map-canvas';
        canvasContainer.appendChild(mapCanvas);
    }
    // Modal (room editor)
    if (!document.getElementById('roomModal')) {
        const modalDiv = document.createElement('div');
        modalDiv.className = 'modal fade';
        modalDiv.id = 'roomModal';
        modalDiv.tabIndex = -1;
        modalDiv.innerHTML = `<div class="modal-dialog modal-lg"><div class="modal-content"><div class="modal-header"><h5 class="modal-title">Room Editor</h5><button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button></div><div class="modal-body"><form id="roomForm"><div class="row"><div class="col-md-6"><div class="mb-3"><label for="roomId" class="form-label">Room ID</label><input type="text" class="form-control" id="roomId" required></div><div class="mb-3"><label for="roomName" class="form-label">Room Name</label><input type="text" class="form-control" id="roomName" required></div><div class="mb-3"><label for="areaSelect" class="form-label">Area</label><select class="form-select" id="areaSelect"><option value="">Select Area</option></select></div></div><div class="col-md-6"><div class="mb-3"><label for="roomX" class="form-label">X Position (East/West)</label><input type="number" class="form-control" id="roomX" value="0"></div><div class="mb-3"><label for="roomY" class="form-label">Y Position (North/South)</label><input type="number" class="form-control" id="roomY" value="0"></div><div class="mb-3"><label for="roomZ" class="form-label">Z Position (Up/Down)</label><input type="number" class="form-control" id="roomZ" value="0"></div></div></div><div class="mb-3"><label for="roomDescription" class="form-label">Description</label><textarea class="form-control" id="roomDescription" rows="4"></textarea></div><div class="mb-3"><div class="d-flex justify-content-between align-items-center mb-2"><label class="form-label mb-0">Exits</label><div class="btn-group btn-group-sm" role="group"><button type="button" class="btn btn-outline-primary" id="selectAllExitsBtn"><i class="fas fa-check-double"></i> Select All</button><button type="button" class="btn btn-outline-secondary" id="clearAllExitsBtn"><i class="fas fa-times"></i> Clear All</button><button type="button" class="btn btn-outline-success" id="autoSelectExitsBtn"><i class="fas fa-magic"></i> Auto Detect</button></div></div><div class="row"><div class="col-md-2"><div class="form-check"><input class="form-check-input" type="checkbox" id="exitNorth"><label class="form-check-label" for="exitNorth">North</label></div></div><div class="col-md-2"><div class="form-check"><input class="form-check-input" type="checkbox" id="exitSouth"><label class="form-check-label" for="exitSouth">South</label></div></div><div class="col-md-2"><div class="form-check"><input class="form-check-input" type="checkbox" id="exitEast"><label class="form-check-label" for="exitEast">East</label></div></div><div class="col-md-2"><div class="form-check"><input class="form-check-input" type="checkbox" id="exitWest"><label class="form-check-label" for="exitWest">West</label></div></div><div class="col-md-2"><div class="form-check"><input class="form-check-input" type="checkbox" id="exitUp"><label class="form-check-label" for="exitUp">Up</label></div></div><div class="col-md-2"><div class="form-check"><input class="form-check-input" type="checkbox" id="exitDown"><label class="form-check-label" for="exitDown">Down</label></div></div></div></div><div class="mb-3"><label for="roomLighting" class="form-label">Lighting</label><select class="form-select" id="roomLighting"><option value="dark">Dark</option><option value="dim">Dim</option><option value="normal" selected>Normal</option><option value="bright">Bright</option></select></div></form></div><div class="modal-footer"><button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button><button type="button" class="btn btn-danger" id="deleteBtn" style="display: none;">Delete</button><button type="button" class="btn btn-primary" id="saveRoomBtn">Save Room</button></div></div></div></div>`;
        document.body.appendChild(modalDiv);
    }
    // Context menu
    if (!document.getElementById('contextMenu')) {
        const ctx = document.createElement('div');
        ctx.id = 'contextMenu';
        ctx.className = 'context-menu';
        ctx.style.display = 'none';
        ctx.innerHTML = `<div class="context-menu-item" id="changeNameContext"><i class="fas fa-edit"></i> Change Name</div>`;
        document.body.appendChild(ctx);
    }
    toggleGridlines();
    // Get API base from template variable
    const apiBase = window.API_BASE || '';
    
    initializeMapBuilder(apiBase);

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
            //renderRoomList();
            //renderMap();
            
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
    }
    document.addEventListener('keydown', handleKeyPress);
    // ...other event listeners as needed...
}

if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', main);
} else {
    main();
}
