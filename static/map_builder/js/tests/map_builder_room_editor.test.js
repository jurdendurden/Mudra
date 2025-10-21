// map_builder_room_editor.test.js
// Unit tests for map_builder_room_editor.js
import {
  populateAreaSelect,
  openRoomEditor,
  saveRoom,
  deleteRoom,
  saveArea,
  saveMap,
  handleExitChange,
  selectAllExits,
  clearAllExits,
  autoSelectExits
} from '../map_builder_room_editor.js';
global.alert = jest.fn();
describe('map_builder_room_editor', () => {
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
  beforeEach(() => {
    global.areas = [{ area_id: 'area_001', name: 'Area 1' }];
    global.rooms = [{ room_id: 'room_001', name: 'Room 1', x: 0, y: 0, z: 0 }];
    global.document = {
      getElementById: jest.fn((id) => ({ value: '', checked: false, innerHTML: '', show: jest.fn(), style: {}, appendChild: jest.fn() })),
      createElement: jest.fn(() => ({ className: '', style: {}, appendChild: jest.fn() })),
      querySelector: jest.fn(() => null)
    };
  });

  test('populateAreaSelect does not throw', () => {
    expect(() => populateAreaSelect()).not.toThrow();
  });

  test('openRoomEditor does not throw', () => {
    expect(() => openRoomEditor(rooms[0])).not.toThrow();
  });

  test('saveRoom does not throw', async () => {
    await expect(saveRoom()).resolves.not.toThrow();
  });

  test('deleteRoom does not throw', async () => {
    await expect(deleteRoom()).resolves.not.toThrow();
  });

  test('saveArea does not throw', async () => {
    await expect(saveArea({ area_id: 'area_002', name: 'Area 2', description: 'desc' })).resolves.not.toThrow();
  });

  test('saveMap does not throw', async () => {
    await expect(saveMap()).resolves.not.toThrow();
  });

  test('handleExitChange does not throw', () => {
    expect(() => handleExitChange('north', true)).not.toThrow();
  });

  test('selectAllExits does not throw', () => {
    expect(() => selectAllExits()).not.toThrow();
  });

  test('clearAllExits does not throw', () => {
    expect(() => clearAllExits()).not.toThrow();
  });

  test('autoSelectExits does not throw', () => {
    expect(() => autoSelectExits()).not.toThrow();
  });
});
