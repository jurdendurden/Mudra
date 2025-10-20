from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json

# Create Flask application for map builder
app = Flask(__name__)

# Get absolute path to database
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'mud_game.db')
# Convert to forward slashes for SQLite URI (works on all platforms)
db_uri = db_path.replace('\\', '/')

# Configuration
app.config['SECRET_KEY'] = 'map-builder-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_uri}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import the db instance from the main app and initialize with this app
from app import db
db.init_app(app)

# Import models from main app
from app.models.room import Room, Area

@app.route('/')
def builder_index():
    """Main map builder interface"""
    # Get all areas and rooms for the builder
    areas = Area.query.all()
    rooms = Room.query.all()
    
    return render_template('map_builder/index.html', areas=areas, rooms=rooms)

@app.route('/api/rooms')
def get_rooms():
    """Get all rooms as JSON"""
    rooms = Room.query.all()
    return jsonify([{
        'id': room.id,
        'room_id': room.room_id,
        'name': room.name,
        'description': room.description,
        'area_id': room.area_id,
        'x': room.x_coord,
        'y': room.y_coord,
        'z': room.z_coord,
        'exits': room.exits,
        'doors': room.doors or {},
        'lighting': room.lighting
    } for room in rooms])

@app.route('/api/areas')
def get_areas():
    """Get all areas as JSON"""
    areas = Area.query.all()
    return jsonify([{
        'id': area.id,
        'area_id': area.area_id,
        'name': area.name,
        'description': area.description
    } for area in areas])

@app.route('/api/rooms', methods=['POST'])
def create_room():
    """Create a new room"""
    data = request.get_json()
    
    # Check for coordinate conflicts
    existing_room = Room.query.filter_by(
        x_coord=data.get('x', 0),
        y_coord=data.get('y', 0),
        z_coord=data.get('z', 0)
    ).first()
    
    if existing_room:
        return jsonify({'error': 'A room already exists at these coordinates'}), 400
    
    room = Room(
        room_id=data['room_id'],
        name=data['name'],
        description=data['description'],
        area_id=data.get('area_id'),
        x_coord=data.get('x', 0),
        y_coord=data.get('y', 0),
        z_coord=data.get('z', 0),
        exits=data.get('exits', {}),
        lighting=data.get('lighting', 'normal')
    )
    
    db.session.add(room)
    db.session.commit()
    
    return jsonify({
        'id': room.id,
        'room_id': room.room_id,
        'name': room.name,
        'description': room.description,
        'area_id': room.area_id,
        'x': room.x_coord,
        'y': room.y_coord,
        'z': room.z_coord,
        'exits': room.exits,
        'doors': room.doors or {},
        'lighting': room.lighting
    })

@app.route('/api/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    """Update an existing room"""
    room = Room.query.get_or_404(room_id)
    data = request.get_json()
    
    # Check for coordinate conflicts (excluding current room)
    if 'x' in data or 'y' in data or 'z' in data:
        x = data.get('x', room.x_coord)
        y = data.get('y', room.y_coord)
        z = data.get('z', room.z_coord)
        
        existing_room = Room.query.filter_by(
            x_coord=x,
            y_coord=y,
            z_coord=z
        ).filter(Room.id != room_id).first()
        
        if existing_room:
            return jsonify({'error': 'A room already exists at these coordinates'}), 400
    
    room.name = data.get('name', room.name)
    room.description = data.get('description', room.description)
    room.area_id = data.get('area_id', room.area_id)
    room.x_coord = data.get('x', room.x_coord)
    room.y_coord = data.get('y', room.y_coord)
    room.z_coord = data.get('z', room.z_coord)
    room.exits = data.get('exits', room.exits)
    room.doors = data.get('doors', room.doors)
    room.lighting = data.get('lighting', room.lighting)
    
    db.session.commit()
    
    return jsonify({
        'id': room.id,
        'room_id': room.room_id,
        'name': room.name,
        'description': room.description,
        'area_id': room.area_id,
        'x': room.x_coord,
        'y': room.y_coord,
        'z': room.z_coord,
        'exits': room.exits,
        'doors': room.doors or {},
        'lighting': room.lighting
    })

@app.route('/api/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    """Delete a room and clean up orphaned exits"""
    room = Room.query.get_or_404(room_id)
    deleted_room_id = room.room_id
    
    # Delete the room
    db.session.delete(room)
    db.session.commit()
    
    # Clean up orphaned exits in other rooms
    all_rooms = Room.query.all()
    for other_room in all_rooms:
        if other_room.exits:
            exits_modified = False
            new_exits = dict(other_room.exits)
            
            # Remove any exits pointing to the deleted room
            for direction, target_room_id in list(new_exits.items()):
                if target_room_id == deleted_room_id:
                    del new_exits[direction]
                    exits_modified = True
            
            # Update room if exits were modified
            if exits_modified:
                other_room.exits = new_exits
                db.session.add(other_room)
    
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/areas', methods=['POST'])
def create_area():
    """Create a new area"""
    data = request.get_json()
    
    area = Area(
        area_id=data['area_id'],
        name=data['name'],
        description=data['description']
    )
    
    db.session.add(area)
    db.session.commit()
    
    return jsonify({
        'id': area.id,
        'area_id': area.area_id,
        'name': area.name,
        'description': area.description
    })

@app.route('/api/rooms/<int:room_id>/doors', methods=['GET'])
def get_room_doors(room_id):
    """Get all doors for a specific room"""
    room = Room.query.get_or_404(room_id)
    return jsonify(room.doors or {})

@app.route('/api/rooms/<int:room_id>/doors/<direction>', methods=['POST', 'PUT'])
def create_or_update_door(room_id, direction):
    """Create or update a door in a specific direction"""
    room = Room.query.get_or_404(room_id)
    data = request.get_json()
    
    # Validate door data
    is_valid, errors = room.validate_door_data(data)
    if not is_valid:
        return jsonify({'error': 'Invalid door data', 'details': errors}), 400
    
    # Add or update the door
    room.add_door(direction, data)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'direction': direction,
        'door': data
    })

@app.route('/api/rooms/<int:room_id>/doors/<direction>', methods=['DELETE'])
def delete_door(room_id, direction):
    """Delete a door from a specific direction"""
    room = Room.query.get_or_404(room_id)
    
    # Remove the door
    room.remove_door(direction)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/keys')
def get_keys():
    """Get all available key templates"""
    keys_file = os.path.join(basedir, 'data', 'items', 'keys.json')
    try:
        with open(keys_file, 'r') as f:
            keys_data = json.load(f)
            return jsonify(keys_data.get('keys', []))
    except FileNotFoundError:
        return jsonify([])

@app.route('/api/doors/validate', methods=['POST'])
def validate_door():
    """Validate door data without saving"""
    data = request.get_json()
    
    # Create a temporary room instance for validation
    temp_room = Room()
    is_valid, errors = temp_room.validate_door_data(data)
    
    return jsonify({
        'valid': is_valid,
        'errors': errors
    })

if __name__ == '__main__':
    # Run the map builder on port 5001
    app.run(debug=True, host='0.0.0.0', port=5001)
