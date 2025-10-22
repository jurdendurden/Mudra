// map_builder.js
// Entry point: imports all modules, initializes app
import { initializeMapBuilder, setRoomModal, roomModal, setDoorModal, doorModal, setSelectedRoom } from './map_builder_core.js';
const apiBase = window.API_BASE || '';
    
initializeMapBuilder(apiBase);
import { fetchAreas, fetchRooms } from './map_builder_api.js';
import { renderAreaList, renderRoomList, renderMap, filterRoomsByArea } from './map_builder_render.js';
import { populateAreaSelect, saveRoom, deleteRoom, saveMap, showDoorHelp, editDoor, updateLockDifficultyLabel, updateDoorButtons, saveDoor, deleteDoor } from './map_builder_room_editor.js';
import { handleRoomDragStart, handleRoomDrop, handleSelectionStart, handleCanvasDrag, handleCanvasMouseUp, handleSelectionEnd, updateMultiSelection, clearMultiSelection, updateCoordDisplay } from './map_builder_canvas.js';
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
        autoExitBtn.addEventListener('click', (e) => {
            e.preventDefault();
            autoExitSelectedRooms();
        });

        // Undo button
        const undoBtn = document.createElement('button');
        undoBtn.className = 'btn btn-secondary btn-sm me-2';
        undoBtn.id = 'undoBtn';
        undoBtn.disabled = true;
        undoBtn.innerHTML = '<i class="fas fa-undo"></i> Undo';
        undoBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            await undoLastAction();
        });

        // Save Map button
        const saveMapBtn = document.createElement('button');
        saveMapBtn.className = 'btn btn-success me-2';
        saveMapBtn.id = 'saveMapBtn';
        saveMapBtn.innerHTML = '<i class="fas fa-save"></i> Save Map';
        saveMapBtn .addEventListener('click', (e) => {
            e.preventDefault();
            saveMap();
        });
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
    let modalDiv = document.getElementById('roomModal');
    
    if (!modalDiv) 
    {
        modalDiv = document.createElement('div');
        modalDiv.className = 'modal fade';
        modalDiv.id = 'roomModal';
        modalDiv.tabIndex = -1;
        document.body.appendChild(modalDiv);
        
    }
    // --- Modal Creation Functions ---
    function createRoomModal() {
    let modalDiv = document.getElementById('roomModal');
            if (!modalDiv) {
                modalDiv = document.createElement('div');
                modalDiv.className = 'modal fade';
                modalDiv.id = 'roomModal';
                modalDiv.tabIndex = -1;
                document.body.appendChild(modalDiv);
            }
            const modalDialog = document.createElement('div');
            modalDialog.className = 'modal-dialog modal-lg';
            const modalContent = document.createElement('div');
            modalContent.className = 'modal-content';
            // Header
            const modalHeader = document.createElement('div');
            modalHeader.className = 'modal-header';
            const modalTitle = document.createElement('h5');
            modalTitle.className = 'modal-title';
            modalTitle.textContent = 'Room Editor';
            const closeBtn = document.createElement('button');
            closeBtn.type = 'button';
            closeBtn.className = 'btn-close btn-close-white';
            closeBtn.setAttribute('data-bs-dismiss', 'modal');
            modalHeader.appendChild(modalTitle);
            modalHeader.appendChild(closeBtn);
            // Body
            const modalBody = document.createElement('div');
            modalBody.className = 'modal-body';
            const roomForm = document.createElement('form');
            roomForm.id = 'roomForm';
            // Row (left/right columns)
            const rowDiv = document.createElement('div');
            rowDiv.className = 'row';
            // Left column
            const colLeft = document.createElement('div');
            colLeft.className = 'col-md-6';
            // Room ID
            const roomIdDiv = document.createElement('div');
            roomIdDiv.className = 'mb-3';
            const roomIdLabel = document.createElement('label');
            roomIdLabel.className = 'form-label';
            roomIdLabel.htmlFor = 'roomId';
            roomIdLabel.textContent = 'Room ID';
            const roomIdInput = document.createElement('input');
            roomIdInput.type = 'text';
            roomIdInput.className = 'form-control';
            roomIdInput.id = 'roomId';
            roomIdInput.required = true;
            roomIdDiv.appendChild(roomIdLabel);
            roomIdDiv.appendChild(roomIdInput);
            // Room Name
            const roomNameDiv = document.createElement('div');
            roomNameDiv.className = 'mb-3';
            const roomNameLabel = document.createElement('label');
            roomNameLabel.className = 'form-label';
            roomNameLabel.htmlFor = 'roomName';
            roomNameLabel.textContent = 'Room Name';
            const roomNameInput = document.createElement('input');
            roomNameInput.type = 'text';
            roomNameInput.className = 'form-control';
            roomNameInput.id = 'roomName';
            roomNameInput.required = true;
            roomNameDiv.appendChild(roomNameLabel);
            roomNameDiv.appendChild(roomNameInput);
            // Area select
            const areaDiv = document.createElement('div');
            areaDiv.className = 'mb-3';
            const areaLabel = document.createElement('label');
            areaLabel.className = 'form-label';
            areaLabel.htmlFor = 'areaSelect';
            areaLabel.textContent = 'Area';
            const areaSelect = document.createElement('select');
            areaSelect.className = 'form-select';
            areaSelect.id = 'areaSelect';
            const defaultAreaOption = document.createElement('option');
            defaultAreaOption.value = '';
            defaultAreaOption.textContent = 'Select Area';
            areaSelect.appendChild(defaultAreaOption);
            areaDiv.appendChild(areaLabel);
            areaDiv.appendChild(areaSelect);
            colLeft.appendChild(roomIdDiv);
            colLeft.appendChild(roomNameDiv);
            colLeft.appendChild(areaDiv);
            // Right column
            const colRight = document.createElement('div');
            colRight.className = 'col-md-6';
            // X Position
            const xDiv = document.createElement('div');
            xDiv.className = 'mb-3';
            const xLabel = document.createElement('label');
            xLabel.className = 'form-label';
            xLabel.htmlFor = 'roomX';
            xLabel.textContent = 'X Position (East/West)';
            const xInput = document.createElement('input');
            xInput.type = 'number';
            xInput.className = 'form-control';
            xInput.id = 'roomX';
            xInput.value = 0;
            xDiv.appendChild(xLabel);
            xDiv.appendChild(xInput);
            // Y Position
            const yDiv = document.createElement('div');
            yDiv.className = 'mb-3';
            const yLabel = document.createElement('label');
            yLabel.className = 'form-label';
            yLabel.htmlFor = 'roomY';
            yLabel.textContent = 'Y Position (North/South)';
            const yInput = document.createElement('input');
            yInput.type = 'number';
            yInput.className = 'form-control';
            yInput.id = 'roomY';
            yInput.value = 0;
            yDiv.appendChild(yLabel);
            yDiv.appendChild(yInput);
            // Z Position
            const zDiv = document.createElement('div');
            zDiv.className = 'mb-3';
            const zLabel = document.createElement('label');
            zLabel.className = 'form-label';
            zLabel.htmlFor = 'roomZ';
            zLabel.textContent = 'Z Position (Up/Down)';
            const zInput = document.createElement('input');
            zInput.type = 'number';
            zInput.className = 'form-control';
            zInput.id = 'roomZ';
            zInput.value = 0;
            zDiv.appendChild(zLabel);
            zDiv.appendChild(zInput);
            colRight.appendChild(xDiv);
            colRight.appendChild(yDiv);
            colRight.appendChild(zDiv);
            rowDiv.appendChild(colLeft);
            rowDiv.appendChild(colRight);
            // Description
            const descDiv = document.createElement('div');
            descDiv.className = 'mb-3';
            const descLabel = document.createElement('label');
            descLabel.className = 'form-label';
            descLabel.htmlFor = 'roomDescription';
            descLabel.textContent = 'Description';
            const descTextarea = document.createElement('textarea');
            descTextarea.className = 'form-control';
            descTextarea.id = 'roomDescription';
            descTextarea.rows = 4;
            descDiv.appendChild(descLabel);
            descDiv.appendChild(descTextarea);
            // Exits
            const exitsDiv = document.createElement('div');
            exitsDiv.className = 'mb-3';
            const exitsHeader = document.createElement('div');
            exitsHeader.className = 'd-flex justify-content-between align-items-center mb-2';
            const exitsLabel = document.createElement('label');
            exitsLabel.className = 'form-label mb-0';
            exitsLabel.textContent = 'Exits';
            const exitsBtnGroup = document.createElement('div');
            exitsBtnGroup.className = 'btn-group btn-group-sm';
            exitsBtnGroup.setAttribute('role', 'group');
            // Select All
            const selectAllBtn = document.createElement('button');
            selectAllBtn.type = 'button';
            selectAllBtn.className = 'btn btn-outline-primary';
            selectAllBtn.id = 'selectAllExitsBtn';
            selectAllBtn.innerHTML = '<i class="fas fa-check-double"></i> Select All';
            // Clear All
            const clearAllBtn = document.createElement('button');
            clearAllBtn.type = 'button';
            clearAllBtn.className = 'btn btn-outline-secondary';
            clearAllBtn.id = 'clearAllExitsBtn';
            clearAllBtn.innerHTML = '<i class="fas fa-times"></i> Clear All';
            // Auto Detect
            const autoDetectBtn = document.createElement('button');
            autoDetectBtn.type = 'button';
            autoDetectBtn.className = 'btn btn-outline-success';
            autoDetectBtn.id = 'autoSelectExitsBtn';
            autoDetectBtn.innerHTML = '<i class="fas fa-magic"></i> Auto Detect';
            exitsBtnGroup.appendChild(selectAllBtn);
            exitsBtnGroup.appendChild(clearAllBtn);
            exitsBtnGroup.appendChild(autoDetectBtn);
            exitsHeader.appendChild(exitsLabel);
            exitsHeader.appendChild(exitsBtnGroup);
            // Exits checkboxes row
            const exitsRow = document.createElement('div');
            exitsRow.className = 'row';
            const exitNames = [
                { id: 'exitNorth', label: 'North' },
                { id: 'exitSouth', label: 'South' },
                { id: 'exitEast', label: 'East' },
                { id: 'exitWest', label: 'West' },
                { id: 'exitUp', label: 'Up' },
                { id: 'exitDown', label: 'Down' }
            ];
            exitNames.forEach(({ id, label }) => {
                const col = document.createElement('div');
                col.className = 'col-4';
                const checkboxDiv = document.createElement('div');
                checkboxDiv.className = 'form-check';
                const checkbox = document.createElement('input');
                checkbox.className = 'form-check-input';
                checkbox.type = 'checkbox';
                checkbox.id = id;
                const labelEl = document.createElement('label');
                labelEl.className = 'form-check-label';
                labelEl.htmlFor = id;
                labelEl.textContent = label;
                checkboxDiv.appendChild(checkbox);
                checkboxDiv.appendChild(labelEl);
                col.appendChild(checkboxDiv);
                exitsRow.appendChild(col);
            });
            exitsDiv.appendChild(exitsHeader);
            exitsDiv.appendChild(exitsRow);
            // Lighting
            const lightingDiv = document.createElement('div');
            lightingDiv.className = 'mb-3';
            const lightingLabel = document.createElement('label');
            lightingLabel.className = 'form-label';
            lightingLabel.htmlFor = 'roomLighting';
            lightingLabel.textContent = 'Lighting';
            const lightingSelect = document.createElement('select');
            lightingSelect.className = 'form-select';
            lightingSelect.id = 'roomLighting';
            const lightingOptions = [
                { value: 'dark', text: 'Dark' },
                { value: 'dim', text: 'Dim' },
                { value: 'normal', text: 'Normal', selected: true },
                { value: 'bright', text: 'Bright' }
            ];
            lightingOptions.forEach(opt => {
                const option = document.createElement('option');
                option.value = opt.value;
                option.textContent = opt.text;
                if (opt.selected) option.selected = true;
                lightingSelect.appendChild(option);
            });
            lightingDiv.appendChild(lightingLabel);
            lightingDiv.appendChild(lightingSelect);
            // --- Doors Section ---
            const doorsDiv = document.createElement('div');
            doorsDiv.className = 'mb-3';
            const doorsHeader = document.createElement('div');
            doorsHeader.className = 'd-flex justify-content-between align-items-center mb-2';
            const doorsLabel = document.createElement('label');
            doorsLabel.className = 'form-label mb-0';
            doorsLabel.textContent = 'Doors';
            const doorsHelpBtn = document.createElement('button');
            doorsHelpBtn.type = 'button';
            doorsHelpBtn.className = 'btn btn-outline-info btn-sm';
            doorsHelpBtn.innerHTML = '<i class="fas fa-question-circle"></i> Help';
            doorsHelpBtn.onclick = showDoorHelp;
            doorsHeader.appendChild(doorsLabel);
            doorsHeader.appendChild(doorsHelpBtn);
            // Row of direction buttons
            const doorsRow = document.createElement('div');
            doorsRow.className = 'row';
            const directions = [
                { dir: 'north', icon: 'fa-arrow-up', label: 'North' },
                { dir: 'south', icon: 'fa-arrow-down', label: 'South' },
                { dir: 'east', icon: 'fa-arrow-right', label: 'East' },
                { dir: 'west', icon: 'fa-arrow-left', label: 'West' },
                { dir: 'up', icon: 'fa-angle-up', label: 'Up' },
                { dir: 'down', icon: 'fa-angle-down', label: 'Down' }
            ];
            directions.forEach(({ dir, icon, label }) => {
                const col = document.createElement('div');
                col.className = 'col-2 text-center';
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'btn btn-outline-warning btn-sm';
                btn.innerHTML = `<i class="fas ${icon}"></i> ${label}`;
                btn.onclick = function() { editDoor(dir); };
                btn.setAttribute('data-direction', dir);
                col.appendChild(btn);
                doorsRow.appendChild(col);
            });
            doorsDiv.appendChild(doorsHeader);
            doorsDiv.appendChild(doorsRow);
            // Assemble form
            roomForm.appendChild(rowDiv);
            roomForm.appendChild(descDiv);
            roomForm.appendChild(exitsDiv);
            roomForm.appendChild(lightingDiv);
            roomForm.appendChild(doorsDiv);
            modalBody.appendChild(roomForm);
            // Footer
            const modalFooter = document.createElement('div');
            modalFooter.className = 'modal-footer';
            const cancelBtn = document.createElement('button');
            cancelBtn.type = 'button';
            cancelBtn.className = 'btn btn-secondary';
            cancelBtn.setAttribute('data-bs-dismiss', 'modal');
            cancelBtn.textContent = 'Cancel';
            cancelBtn.addEventListener('click', () => { 
                setSelectedRoom(null);
            });
            const deleteBtn = document.createElement('button');
            deleteBtn.type = 'button';
            deleteBtn.className = 'btn btn-danger';
            deleteBtn.id = 'deleteBtn';
            deleteBtn.style.display = 'none';
            deleteBtn.textContent = 'Delete';
            deleteBtn.addEventListener('click', deleteRoom);
            const saveBtn = document.createElement('button');
            saveBtn.type = 'button';
            saveBtn.className = 'btn btn-primary';
            saveBtn.id = 'saveRoomBtn';
            saveBtn.textContent = 'Save Room';
            saveBtn.addEventListener('click', saveRoom);
            modalFooter.appendChild(cancelBtn);
            modalFooter.appendChild(deleteBtn);
            modalFooter.appendChild(saveBtn);
            // Assemble modal
            modalContent.appendChild(modalHeader);
            modalContent.appendChild(modalBody);
            modalContent.appendChild(modalFooter);
            modalDialog.appendChild(modalContent);
            modalDiv.innerHTML = '';
            modalDiv.appendChild(modalDialog);
            setRoomModal(new bootstrap.Modal(modalDiv));
        }

        function createDoorModal() {
            let modalDiv = document.getElementById('doorModal');
            if (!modalDiv) {
                modalDiv = document.createElement('div');
                modalDiv.className = 'modal fade';
                modalDiv.id = 'doorModal';
                modalDiv.tabIndex = -1;
                document.body.appendChild(modalDiv);
            }
            const modalDialog = document.createElement('div');
            modalDialog.className = 'modal-dialog modal-lg';
            const modalContent = document.createElement('div');
            modalContent.className = 'modal-content';
            // Header
            const modalHeader = document.createElement('div');
            modalHeader.className = 'modal-header';
            const modalTitle = document.createElement('h5');
            modalTitle.className = 'modal-title';
            modalTitle.id = 'doorDirection';
            modalTitle.textContent = 'Door Editor';
            const closeBtn = document.createElement('button');
            closeBtn.type = 'button';
            closeBtn.className = 'btn-close btn-close-white';
            closeBtn.setAttribute('data-bs-dismiss', 'modal');
            modalHeader.appendChild(modalTitle);
            modalHeader.appendChild(closeBtn);
            // Body
            const modalBody = document.createElement('div');
            modalBody.className = 'modal-body';
            const doorForm = document.createElement('form');
            doorForm.id = 'doorForm';
            // Door ID
            const doorIdDiv = document.createElement('div');
            doorIdDiv.className = 'mb-3';
            const doorIdLabel = document.createElement('label');
            doorIdLabel.className = 'form-label';
            doorIdLabel.htmlFor = 'doorId';
            doorIdLabel.textContent = 'Door ID';
            const doorIdInput = document.createElement('input');
            doorIdInput.type = 'text';
            doorIdInput.className = 'form-control';
            doorIdInput.id = 'doorId';
            doorIdInput.required = true;
            doorIdDiv.appendChild(doorIdLabel);
            doorIdDiv.appendChild(doorIdInput);
            // Door Name
            const doorNameDiv = document.createElement('div');
            doorNameDiv.className = 'mb-3';
            const doorNameLabel = document.createElement('label');
            doorNameLabel.className = 'form-label';
            doorNameLabel.htmlFor = 'doorName';
            doorNameLabel.textContent = 'Door Name';
            const doorNameInput = document.createElement('input');
            doorNameInput.type = 'text';
            doorNameInput.className = 'form-control';
            doorNameInput.id = 'doorName';
            doorNameInput.required = true;
            doorNameDiv.appendChild(doorNameLabel);
            doorNameDiv.appendChild(doorNameInput);
            // Door Description
            const doorDescDiv = document.createElement('div');
            doorDescDiv.className = 'mb-3';
            const doorDescLabel = document.createElement('label');
            doorDescLabel.className = 'form-label';
            doorDescLabel.htmlFor = 'doorDescription';
            doorDescLabel.textContent = 'Description';
            const doorDescInput = document.createElement('textarea');
            doorDescInput.className = 'form-control';
            doorDescInput.id = 'doorDescription';
            doorDescInput.rows = 2;
            doorDescDiv.appendChild(doorDescLabel);
            doorDescDiv.appendChild(doorDescInput);
            // Key Template
            const keyDiv = document.createElement('div');
            keyDiv.className = 'mb-3';
            const keyLabel = document.createElement('label');
            keyLabel.className = 'form-label';
            keyLabel.htmlFor = 'doorKeyId';
            keyLabel.textContent = 'Key Template';
            const keySelect = document.createElement('select');
            keySelect.className = 'form-select';
            keySelect.id = 'doorKeyId';
            keyDiv.appendChild(keyLabel);
            keyDiv.appendChild(keySelect);
            // Lock Difficulty
            const lockDiv = document.createElement('div');
            lockDiv.className = 'mb-3';
            const lockLabel = document.createElement('label');
            lockLabel.className = 'form-label';
            lockLabel.htmlFor = 'doorLockDifficulty';
            lockLabel.textContent = 'Lock Difficulty';
            const lockInput = document.createElement('input');
            lockInput.type = 'number';
            lockInput.className = 'form-control';
            lockInput.id = 'doorLockDifficulty';
            lockInput.value = 0;
            lockInput.min = 0;
            lockInput.max = 255;
            lockInput.step = 1;
            lockDiv.appendChild(lockLabel);
            lockDiv.appendChild(lockInput);
            // Lock Difficulty Value
            const lockValueSpan = document.createElement('span');
            lockValueSpan.id = 'lockDifficultyValue';
            lockValueSpan.className = 'ms-2 text-info';
            lockDiv.appendChild(lockValueSpan);
            // Flags
            const flagsDiv = document.createElement('div');
            flagsDiv.className = 'mb-3';
            const flagsLabel = document.createElement('label');
            flagsLabel.className = 'form-label';
            flagsLabel.textContent = 'Flags';
            flagsDiv.appendChild(flagsLabel);
            const flagsRow = document.createElement('div');
            flagsRow.className = 'row';
            const flagOptions = [
                { id: 'flagClosed', label: 'Closed' },
                { id: 'flagLocked', label: 'Locked' },
                { id: 'flagPickProof', label: 'Pick Proof' },
                { id: 'flagPassProof', label: 'Pass Proof' },
                { id: 'flagSecret', label: 'Secret' },
                { id: 'flagHidden', label: 'Hidden' },
                { id: 'flagNoLock', label: 'No Lock' },
                { id: 'flagNoKnock', label: 'No Knock' },
                { id: 'flagNoClose', label: 'No Close' }
            ];
            flagOptions.forEach(({ id, label }) => {
                const col = document.createElement('div');
                col.className = 'col-4';
                const checkboxDiv = document.createElement('div');
                checkboxDiv.className = 'form-check';
                const checkbox = document.createElement('input');
                checkbox.className = 'form-check-input';
                checkbox.type = 'checkbox';
                checkbox.id = id;
                const labelEl = document.createElement('label');
                labelEl.className = 'form-check-label';
                labelEl.htmlFor = id;
                labelEl.textContent = label;
                checkboxDiv.appendChild(checkbox);
                checkboxDiv.appendChild(labelEl);
                col.appendChild(checkboxDiv);
                flagsRow.appendChild(col);
            });
            flagsDiv.appendChild(flagsRow);
            // Assemble form
            doorForm.appendChild(doorIdDiv);
            doorForm.appendChild(doorNameDiv);
            doorForm.appendChild(doorDescDiv);
            doorForm.appendChild(keyDiv);
            doorForm.appendChild(lockDiv);
            doorForm.appendChild(flagsDiv);
            modalBody.appendChild(doorForm);
            // Footer
            const modalFooter = document.createElement('div');
            modalFooter.className = 'modal-footer';
            const cancelBtn = document.createElement('button');
            cancelBtn.type = 'button';
            cancelBtn.className = 'btn btn-secondary';
            cancelBtn.setAttribute('data-bs-dismiss', 'modal');
            cancelBtn.textContent = 'Cancel';
            const deleteBtn = document.createElement('button');
            deleteBtn.type = 'button';
            deleteBtn.className = 'btn btn-danger';
            deleteBtn.id = 'deleteDoorBtn';
            deleteBtn.textContent = 'Delete';
            deleteBtn.style.display = 'none';
            deleteBtn.onclick = deleteDoor;
            const saveBtn = document.createElement('button');
            saveBtn.type = 'button';
            saveBtn.className = 'btn btn-primary';
            saveBtn.id = 'saveDoorBtn';
            saveBtn.textContent = 'Save Door';
            saveBtn.onclick = saveDoor;
            modalFooter.appendChild(cancelBtn);
            modalFooter.appendChild(deleteBtn);
            modalFooter.appendChild(saveBtn);
            // Assemble modal
            modalContent.appendChild(modalHeader);
            modalContent.appendChild(modalBody);
            modalContent.appendChild(modalFooter);
            modalDialog.appendChild(modalContent);
            modalDiv.innerHTML = '';
            modalDiv.appendChild(modalDialog);
            setDoorModal(new bootstrap.Modal(modalDiv));
        }

        // Create modals
        createRoomModal();
        createDoorModal();
    
    // Context menu
    if (!document.getElementById('contextMenu')) {
        const ctx = document.createElement('div');
        ctx.id = 'contextMenu';
        ctx.className = 'context-menu';
        ctx.style.display = 'none';
        ctx.innerHTML = `<div class="context-menu-item" id="changeNameContext"><i class="fas fa-edit"></i> Change Name</div>`;
        document.body.appendChild(ctx);
    }

    const coordDisplay = document.createElement('div');
    coordDisplay.className = 'coord-display';
    coordDisplay.id = 'coord-display';
    coordDisplay.textContent = 'X: 0, Y: 0, Z: 0';
    document.body.appendChild(coordDisplay);

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
