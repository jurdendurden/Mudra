from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import json

# Create Flask application for map builder
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'map-builder-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/mud_game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Import models from main app
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
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
        'exits': room.exits
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
    
    room = Room(
        room_id=data['room_id'],
        name=data['name'],
        description=data['description'],
        area_id=data.get('area_id'),
        x_coord=data.get('x', 0),
        y_coord=data.get('y', 0),
        exits=data.get('exits', {})
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
        'exits': room.exits
    })

@app.route('/api/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    """Update an existing room"""
    room = Room.query.get_or_404(room_id)
    data = request.get_json()
    
    room.name = data.get('name', room.name)
    room.description = data.get('description', room.description)
    room.area_id = data.get('area_id', room.area_id)
    room.x_coord = data.get('x', room.x_coord)
    room.y_coord = data.get('y', room.y_coord)
    room.exits = data.get('exits', room.exits)
    
    db.session.commit()
    
    return jsonify({
        'id': room.id,
        'room_id': room.room_id,
        'name': room.name,
        'description': room.description,
        'area_id': room.area_id,
        'x': room.x_coord,
        'y': room.y_coord,
        'exits': room.exits
    })

@app.route('/api/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    """Delete a room"""
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
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

if __name__ == '__main__':
    # Run the map builder on port 5001
    app.run(debug=True, host='0.0.0.0', port=5001)
