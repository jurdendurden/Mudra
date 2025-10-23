# Map Builder JS Modularization Plan

This checklist tracks the extraction and modularization of JavaScript from `index.html` into ES6 modules under `static/map_builder/js/`. Tick off each item as it is completed.

---

## Core Modules


- [x] **map_builder_core.js**
  - Initialization, global state, API base setup, main entry point

- [x] **map_builder_api.js**
  - API communication: load/save rooms/areas, fetch wrappers

- [x] **map_builder_render.js**
  - Rendering: map, sidebar, tooltips, gridlines, coordinate labels (stubs only, needs implementation)

- [x] **map_builder_room_editor.js**
  - Room/area modal logic, exit management, dropdown population (stubs only, needs implementation)

- [x] **map_builder_canvas.js**
  - Canvas interaction: drag-and-drop, selection, mouse/keyboard events, coordinate display (stubs only, needs implementation)

- [x] **map_builder_undo.js**
  - Undo/redo stack, action history, undo button state (stubs only, needs implementation)

- [x] **map_builder_context.js**
  - Context menu logic, keyboard shortcuts, batch actions (stubs only, needs implementation)

- [x] **map_builder_utils.js**
  - Helper functions, shared constants (stubs only, needs implementation)

- [x] **map_builder.js**
  - Entry point: imports all modules, initializes app

---

## Setup Steps


- [x] Create folder structure: `static/map_builder/js/`
- [x] Update HTML to load only the main bundle or entry point

---



**Next Steps:**
- Implement the actual logic for each stubbed function in the modules above.
  - [ ] Rendering logic is being added to `map_builder_render.js` from the original inline script in `all-in-one-index.html`.
- Test and debug the modularized app in the browser.
- Gradually remove any remaining dependencies on the old inline script.

**Reference:**
- A copy of the old all-in-one template is preserved in `templates/map_builder/all-in-one-index.html` for future reference.

**Check off each module and step as you complete them!**
