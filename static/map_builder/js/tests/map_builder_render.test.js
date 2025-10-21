// map_builder_render.test.js
// Unit tests for map_builder_render.js
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

import { setRooms, setAreas } from '../map_builder_core.js';
import {
  renderAreaList,
  renderRoomList,
  renderMap,
  showTooltip,
  hideTooltip,
  updateTooltipPosition,
  toggleGridlines,
  toggleCoordinateLabels,
  updateGridAlignment
} from '../map_builder_render.js';

describe('map_builder_render', () => {
  beforeEach(() => {
    setAreas([{ area_id: 'area_001', name: 'Area 1' }]);
    setRooms = [{ room_id: 'room_001', name: 'Room 1', x: 0, y: 0, z: 0 }];
    global.document = {
      getElementById: jest.fn((id) => ({ innerHTML: '', value: 'all', checked: false, addEventListener: jest.fn(), querySelectorAll: jest.fn(() => []) })),
      createElement: jest.fn(() => ({ className: '', style: {}, appendChild: jest.fn(), remove: jest.fn() })),
      querySelector: jest.fn(() => null)
    };
  });

  test('renderAreaList does not throw', () => {
    expect(() => renderAreaList()).not.toThrow();
  });

  test('renderRoomList does not throw', () => {
    expect(() => renderRoomList()).not.toThrow();
  });

  test('renderMap does not throw', () => {
    expect(() => renderMap()).not.toThrow();
  });

  test('showTooltip does not throw', () => {
    const event = { pageX: 0, pageY: 0 };
    expect(() => showTooltip(event, rooms[0])).not.toThrow();
  });

  test('hideTooltip does not throw', () => {
    expect(() => hideTooltip()).not.toThrow();
  });

  test('updateTooltipPosition does not throw', () => {
    const event = { pageX: 0, pageY: 0 };
    expect(() => updateTooltipPosition(event)).not.toThrow();
  });

  test('toggleGridlines does not throw', () => {
    expect(() => toggleGridlines()).not.toThrow();
  });

  test('toggleCoordinateLabels does not throw', () => {
    expect(() => toggleCoordinateLabels()).not.toThrow();
  });

  test('updateGridAlignment does not throw', () => {
    expect(() => updateGridAlignment()).not.toThrow();
  });
});
