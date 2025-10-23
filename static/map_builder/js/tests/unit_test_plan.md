# 🧪 Map Builder JS Unit Test Plan

This checklist outlines the recommended order and scope for writing unit tests for the Map Builder JS modules. Each item and subitem can be checked off as tests are implemented.

## 1. Core Utilities
- [x] **map_builder_utils.js**
  - [x] `deepCopy` function
  - [x] `getNextRoomId` function
  - [x] `getOppositeDirection` function

## 2. API Layer
- [x] **map_builder_api.js**
  - [x] `fetchAreas`
  - [x] `fetchRooms`
  - [x] `createRoom`
  - [x] `updateRoom`
  - [x] `deleteRoom`
  - [x] `createArea`

## 3. State Management
- [x] **map_builder_core.js**
  - [x] Global state setters/getters
  - [x] `initializeMapBuilder`

## 4. Undo/Redo Logic
- [x] **map_builder_undo.js**
  - [x] `addToUndoHistory`
  - [x] `updateUndoButton`
  - [x] `undoLastAction`

## 5. Canvas Interaction
- [x] **map_builder_canvas.js**
  - [x] `handleCanvasClick`
  - [x] `handleKeyPress`
  - [x] `handleRoomDragStart`
  - [x] `handleRoomDrop`
  - [x] Selection/drag helpers

## 6. Context Menu & Batch Actions
- [x] **map_builder_context.js**
  - [x] `handleContextMenu`
  - [x] `createAutoRoom`
  - [x] Batch actions (copy, delete, auto-exit, rename)
  - [x] Keyboard shortcuts

## 7. Rendering Logic
- [x] **map_builder_render.js**
  - [x] `renderAreaList`
  - [x] `renderRoomList`
  - [x] `renderMap`
  - [x] Tooltip/gridline/selection helpers

## 8. Room Editor Modal
- [x] **map_builder_room_editor.js**
  - [x] `populateAreaSelect`
  - [x] `openRoomEditor`
  - [x] `saveRoom`
  - [x] Exit management stubs
  - [x] `deleteRoom`
  - [x] `saveArea`
  - [x] `saveMap`

---

## Suggested Order for Writing Tests
1. **Start with core utilities** (map_builder_utils.js)
2. **API layer** (map_builder_api.js) — mock fetch
3. **State management** (map_builder_core.js)
4. **Undo/redo logic** (map_builder_undo.js)
5. **Canvas interaction** (map_builder_canvas.js)
6. **Context menu & batch actions** (map_builder_context.js)
7. **Rendering logic** (map_builder_render.js)
8. **Room editor modal** (map_builder_room_editor.js)

---

## Notes
- Use [Jest](https://jestjs.io/) or [Vitest](https://vitest.dev/) for unit testing.
- Mock DOM and fetch APIs as needed.
- Focus on pure functions first, then event handlers and UI logic.
- Update this checklist as tests are added.
