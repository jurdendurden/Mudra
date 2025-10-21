// map_builder_canvas.test.js
// Unit tests for map_builder_canvas.js
import {
  handleCanvasClick,
  handleKeyPress,
  handleRoomDragStart,
  handleRoomDrop
} from '../map_builder_canvas.js';

// Mocks for DOM and global state
beforeEach(() => {
  global.rooms = [];
  global.selectedRoom = null;
  global.autoRoomMode = true;
  global.isDraggingRoom = false;
  global.isSelecting = false;
  global.window = {};
});
global.alert = jest.fn();
describe('map_builder_canvas', () => {
  test('handleCanvasClick creates room at position', async () => {
    // Mock event and DOM
    const event = {
      currentTarget: { getBoundingClientRect: () => ({ left: 0, top: 0 }), scrollLeft: 0, scrollTop: 0 },
      clientX: 1050,
      clientY: 950,
      target: { classList: { contains: () => false } }
    };
    global.rooms = [];
    global.document = {
      getElementById: jest.fn((id) => ({ value: 'all' }))
    };
    // Should not throw
    await expect(handleCanvasClick(event)).resolves.not.toThrow();
  });

  test('handleKeyPress does nothing if autoRoomMode is off', async () => {
    global.autoRoomMode = false;
    const event = { code: 'Numpad8', preventDefault: jest.fn() };
    await expect(handleKeyPress(event)).resolves.toBeUndefined();
  });

  test('handleRoomDragStart only allows drag with Ctrl', () => {
    const event = { ctrlKey: false };
    expect(() => handleRoomDragStart(event, {}, {})).not.toThrow();
  });

  test('handleRoomDrop resets drag state', async () => {
    global.isDraggingRoom = true;
    global.draggedRoom = { x: 0, y: 0 };
    global.draggedNode = {};
    global.draggedRooms = [{ x: 0, y: 0 }];
    global.draggedNodes = [{ node: {} }];
    global.dragOffset = { x: 0, y: 0 };
    global.window = {};
    global.document = {
      getElementById: jest.fn(() => ({ getBoundingClientRect: () => ({ left: 0, top: 0 }), scrollLeft: 0, scrollTop: 0 }))
    };
    await expect(handleRoomDrop({ clientX: 1050, clientY: 950 })).resolves.not.toThrow();
  });
});
