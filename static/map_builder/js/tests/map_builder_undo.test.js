// map_builder_undo.test.js
// Unit tests for map_builder_undo.js
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
global.alert = jest.fn();
import {
  addToUndoHistory,
  updateUndoButton,
  undoLastAction
} from '../map_builder_undo.js';

import { setUndoHistory, undoHistory, MAX_UNDO_STEPS } from '../map_builder_core.js';

// Mocks for DOM and API
beforeAll(() => {
  global.document = {
    getElementById: jest.fn(() => ({ disabled: false }))
  };
});

describe('map_builder_undo', () => {
  test('addToUndoHistory adds actions and trims history', () => {
    setUndoHistory([]);
    addToUndoHistory({ type: 'create', room: { id: 1 } });
    addToUndoHistory({ type: 'update', room: { id: 2 } });
    addToUndoHistory({ type: 'delete', room: { id: 3 } });
    addToUndoHistory({ type: 'bulk', actions: [] });
    expect(undoHistory.length).toBe(MAX_UNDO_STEPS);
  });

  test('updateUndoButton disables button if history empty', () => {
    const btn = { disabled: false };
    document.getElementById.mockReturnValueOnce(btn);
    setUndoHistory([]);
    updateUndoButton();
    expect(btn.disabled).toBe(true);
  });

  // Note: undoLastAction requires more integration/mocking for async API calls
});
