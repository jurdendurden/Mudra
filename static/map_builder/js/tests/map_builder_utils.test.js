// map_builder_utils.test.js
// Unit tests for map_builder_utils.js
import { deepCopy, getNextRoomId, getOppositeDirection } from '../map_builder_utils.js';
global.alert = jest.fn();
describe('map_builder_utils', () => {
  test('deepCopy creates a deep clone', () => {
    const obj = { a: 1, b: { c: 2 } };
    const clone = deepCopy(obj);
    expect(clone).toEqual(obj);
    expect(clone).not.toBe(obj);
    expect(clone.b).not.toBe(obj.b);
  });

  test('getNextRoomId returns correct next id', () => {
    // Mock rooms array
    const rooms = [
      { room_id: 'room_001' },
      { room_id: 'room_002' },
      { room_id: 'room_004' }
    ];
    global.rooms = rooms;
    expect(getNextRoomId()).toBe('room_003');
  });

  test('getOppositeDirection returns correct direction', () => {
    expect(getOppositeDirection('north')).toBe('south');
    expect(getOppositeDirection('southeast')).toBe('northwest');
    expect(getOppositeDirection('up')).toBe('down');
    expect(getOppositeDirection('invalid')).toBeNull();
  });
});
