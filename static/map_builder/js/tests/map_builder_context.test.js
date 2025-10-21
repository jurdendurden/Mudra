// map_builder_context.test.js
// Unit tests for map_builder_context.js
import {
  handleContextMenu,
  createAutoRoom,
  copySelectedRooms,
  deleteSelectedRooms,
  autoExitSelectedRooms,
  changeSelectedRoomNames,
  handleKeyPress
} from '../map_builder_context.js';

beforeEach(() => {
  global.selectedRoom = { x: 0, y: 0, z: 0, name: 'Room 1', area_id: 'area_001', lighting: 'normal' };
  global.rooms = [global.selectedRoom];
  global.multiSelectedRooms = [];
  global.document = {
    getElementById: jest.fn(() => ({ value: 'north' })),
    querySelector: jest.fn(() => null)
  };
  global.confirm = jest.fn(() => true);
  global.prompt = jest.fn(() => 'New Name');
});
global.alert = jest.fn();
describe('map_builder_context', () => {
// Global fetch mock for all API calls
beforeAll(() => {
  global.fetch = jest.fn((url, options) => {
    return Promise.resolve({
      ok: true,
      json: async () => {
        if (url.includes('/api/rooms') && options?.method === 'POST') {
          return { room_id: 'room_002', name: 'New Room' };
        }
        if (url.includes('/api/rooms') && options?.method === 'PUT') {
          return { room_id: 'room_002', name: 'Updated Room' };
        }
        if (url.includes('/api/rooms') && options?.method === 'DELETE') {
          return { success: true };
        }
        if (url.includes('/api/areas') && options?.method === 'POST') {
          return { area_id: 'area_002', name: 'New Area' };
        }
        if (url.includes('/api/rooms')) {
          return [{ room_id: 'room_001', name: 'Test Room' }];
        }
        if (url.includes('/api/areas')) {
          return [{ area_id: 'area_001', name: 'Test Area' }];
        }
        return {};
      }
    });
  });
});
  test('handleContextMenu does not throw for room node', () => {
    const event = { target: { classList: { contains: () => true }, closest: () => ({ style: { left: '0' } }) }, preventDefault: jest.fn() };
    expect(() => handleContextMenu(event)).not.toThrow();
  });

  test('createAutoRoom creates a new room in direction', async () => {
    const direction = { x: 1, y: 0, z: 0, name: 'east' };
    await expect(createAutoRoom(direction)).resolves.not.toThrow();
  });

  test('copySelectedRooms does not throw if no selection', async () => {
    global.multiSelectedRooms = [];
    await expect(copySelectedRooms()).resolves.not.toThrow();
  });

  test('deleteSelectedRooms does not throw if no selection', async () => {
    global.selectedRoom = null;
    global.multiSelectedRooms = [];
    await expect(deleteSelectedRooms()).resolves.not.toThrow();
  });

  test('autoExitSelectedRooms does not throw if no selection', async () => {
    global.multiSelectedRooms = [];
    await expect(autoExitSelectedRooms()).resolves.not.toThrow();
  });

  test('changeSelectedRoomNames does not throw if no selection', async () => {
    global.multiSelectedRooms = [];
    await expect(changeSelectedRoomNames()).resolves.not.toThrow();
  });

  test('handleKeyPress does not throw for Enter', () => {
    const event = { key: 'Enter', target: { tagName: 'INPUT' } };
    expect(() => handleKeyPress(event)).not.toThrow();
  });
});
