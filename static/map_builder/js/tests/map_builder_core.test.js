// map_builder_core.test.js
// Unit tests for map_builder_core.js
import {
  setRooms,
  setAreas,
  setSelectedRoom,
  setRoomModal,
  setTooltip,
  setMultiSelectedRooms,
  setIsSelecting,
  setSelectionStart,
  setJustFinishedDrag,
  setIsDraggingRoom,
  setDraggedRoom,
  setDraggedNode,
  setDraggedRooms,
  setDraggedNodes,
  setDragOffset,
  setUndoHistory,
  setAutoRoomMode,
  setAPIBase,
  initializeMapBuilder,
  rooms,
  areas,
  selectedRoom,
  roomModal,
  tooltip,
  multiSelectedRooms,
  isSelecting,
  selectionStart,
  justFinishedDrag,
  isDraggingRoom,
  draggedRoom,
  draggedNode,
  draggedRooms,
  draggedNodes,
  dragOffset,
  undoHistory,
  autoRoomMode,
  API_BASE
} from '../map_builder_core.js';
global.alert = jest.fn();
describe('map_builder_core', () => {
  test('setters update global state', () => {
    setRooms([{ room_id: 'room_001' }]);
    expect(rooms).toEqual([{ room_id: 'room_001' }]);
    setAreas([{ area_id: 'area_001' }]);
    expect(areas).toEqual([{ area_id: 'area_001' }]);
    setSelectedRoom({ room_id: 'room_001' });
    expect(selectedRoom).toEqual({ room_id: 'room_001' });
    setMultiSelectedRooms(['room_001']);
    expect(multiSelectedRooms).toEqual(['room_001']);
    setIsSelecting(true);
    expect(isSelecting).toBe(true);
    setSelectionStart({ x: 1, y: 2 });
    expect(selectionStart).toEqual({ x: 1, y: 2 });
    setJustFinishedDrag(true);
    expect(justFinishedDrag).toBe(true);
    setIsDraggingRoom(true);
    expect(isDraggingRoom).toBe(true);
    setDraggedRoom({ room_id: 'room_002' });
    expect(draggedRoom).toEqual({ room_id: 'room_002' });
    setDraggedNode({});
    expect(draggedNode).toEqual({});
    setDraggedRooms([{ room_id: 'room_003' }]);
    expect(draggedRooms).toEqual([{ room_id: 'room_003' }]);
    setDraggedNodes([{}]);
    expect(draggedNodes).toEqual([{}]);
    setDragOffset({ x: 5, y: 6 });
    expect(dragOffset).toEqual({ x: 5, y: 6 });
    setUndoHistory(['action']);
    expect(undoHistory).toEqual(['action']);
    setAutoRoomMode(false);
    expect(autoRoomMode).toBe(false);
    setAPIBase('test_base');
    expect(API_BASE).toBe('test_base');
  });

  test('initializeMapBuilder sets API_BASE', () => {
    initializeMapBuilder('my_api_base');
    expect(API_BASE).toBe('my_api_base');
  });
});
