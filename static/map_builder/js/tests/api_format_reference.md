# 🗂️ API Format Reference for Map Builder JS Tests

This document summarizes the API endpoints and expected request/response formats for the map builder backend (`map_builder.py`). Use this as a reference when mocking API calls in JS unit tests.

---

## Endpoints & Formats

### 1. Get All Rooms
- **GET** `/api/rooms`
- **Response:**
  ```json
  [
    {
      "id": 1,
      "room_id": "room_001",
      "name": "Room Name",
      "description": "...",
      "area_id": "area_001",
      "x": 0,
      "y": 0,
      "z": 0,
      "exits": {"north": "room_002"},
      "lighting": "normal"
    },
    ...
  ]
  ```

### 2. Get All Areas
- **GET** `/api/areas`
- **Response:**
  ```json
  [
    {
      "id": 1,
      "area_id": "area_001",
      "name": "Area Name",
      "description": "..."
    },
    ...
  ]
  ```

### 3. Create Room
- **POST** `/api/rooms`
- **Request Body:**
  ```json
  {
    "room_id": "room_002",
    "name": "Room Name",
    "description": "...",
    "area_id": "area_001",
    "x": 1,
    "y": 0,
    "z": 0,
    "exits": {"south": "room_001"},
    "lighting": "normal"
  }
  ```
- **Response:** Same as GET `/api/rooms` (single room object)
- **Error:** `{ "error": "A room already exists at these coordinates" }`

### 4. Update Room
- **PUT** `/api/rooms/<int:room_id>`
- **Request Body:**
  ```json
  {
    "name": "New Name",
    "description": "...",
    "area_id": "area_001",
    "x": 1,
    "y": 0,
    "z": 0,
    "exits": {"north": "room_003"},
    "lighting": "dim"
  }
  ```
- **Response:** Same as GET `/api/rooms` (single room object)
- **Error:** `{ "error": "A room already exists at these coordinates" }`

### 5. Delete Room
- **DELETE** `/api/rooms/<int:room_id>`
- **Response:** `{ "success": true }`

### 6. Create Area
- **POST** `/api/areas`
- **Request Body:**
  ```json
  {
    "area_id": "area_002",
    "name": "New Area",
    "description": "..."
  }
  ```
- **Response:**
  ```json
  {
    "id": 2,
    "area_id": "area_002",
    "name": "New Area",
    "description": "..."
  }
  ```

---

## Notes
- All responses are JSON.
- Room coordinates: `x`, `y`, `z` (integers)
- Room exits: `{ "direction": "room_id" }`
- Area IDs and Room IDs are strings (e.g., `area_001`, `room_001`).
- Error responses use `{ "error": "..." }` with HTTP 400 status.

Use this reference to mock fetch calls and validate request/response structures in your JS unit tests.
