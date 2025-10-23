// map_builder_api.test.js
// Unit tests for map_builder_api.js
import {
  fetchAreas,
  fetchRooms,
  createRoom,
  updateRoom,
  deleteRoom,
  createArea
} from '../map_builder_api.js';

// Use jest-fetch-mock or similar to mock fetch
beforeAll(() => {
  global.fetch = jest.fn();
});

afterEach(() => {
  fetch.mockClear();
});
global.alert = jest.fn();
describe('map_builder_api', () => {
  test('fetchAreas returns area list', async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ([{ area_id: 'area_001', name: 'Test Area' }]) });
    const areas = await fetchAreas();
    expect(areas).toEqual([{ area_id: 'area_001', name: 'Test Area' }]);
  });

  test('fetchRooms returns room list', async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ([{ room_id: 'room_001', name: 'Test Room' }]) });
    const rooms = await fetchRooms();
    expect(rooms).toEqual([{ room_id: 'room_001', name: 'Test Room' }]);
  });

  test('createRoom posts data and returns room', async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ({ room_id: 'room_002', name: 'New Room' }) });
    const room = await createRoom({ room_id: 'room_002', name: 'New Room' });
    expect(room).toEqual({ room_id: 'room_002', name: 'New Room' });
    expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/api/rooms'), expect.objectContaining({ method: 'POST' }));
  });

  test('updateRoom puts data and returns room', async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ({ room_id: 'room_002', name: 'Updated Room' }) });
    const room = await updateRoom('room_002', { name: 'Updated Room' });
    expect(room).toEqual({ room_id: 'room_002', name: 'Updated Room' });
    expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/api/rooms/room_002'), expect.objectContaining({ method: 'PUT' }));
  });

  test('deleteRoom deletes and returns result', async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ({ success: true }) });
    const result = await deleteRoom('room_002');
    expect(result).toEqual({ success: true });
    expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/api/rooms/room_002'), expect.objectContaining({ method: 'DELETE' }));
  });

  test('createArea posts data and returns area', async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => ({ area_id: 'area_002', name: 'New Area' }) });
    const area = await createArea({ area_id: 'area_002', name: 'New Area' });
    expect(area).toEqual({ area_id: 'area_002', name: 'New Area' });
    expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/api/areas'), expect.objectContaining({ method: 'POST' }));
  });
});
