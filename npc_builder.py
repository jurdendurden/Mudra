from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json

# Create Flask application for NPC builder
app = Flask(__name__)

# Get absolute path to database
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'mud_game.db')
# Convert to forward slashes for SQLite URI (works on all platforms)
db_uri = db_path.replace('\\', '/')

# Configuration
app.config['SECRET_KEY'] = 'npc-builder-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_uri}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import the db instance from the main app and initialize with this app
from app import db
db.init_app(app)

# Import models from main app
from app.models.npc import NPC
from app.models.room import Room, Area
from app.utils.race_loader import get_all_races

@app.route('/')
def builder_index():
    """Main NPC builder interface"""
    # Get all NPCs for the builder
    npcs = NPC.query.all()
    rooms = Room.query.all()
    areas = Area.query.all()
    races = get_all_races()
    
    # Load skills and spells data
    skills_data = load_skills_data()
    spells_data = load_spells_data()
    
    return render_template('npc_builder/index.html', 
                          npcs=npcs, 
                          rooms=rooms,
                          areas=areas,
                          races=sorted(races),
                          skills=skills_data,
                          spells=spells_data)

def load_skills_data():
    """Load skills from JSON file"""
    skills_file = os.path.join(basedir, 'data', 'skills', 'skills.json')
    try:
        with open(skills_file, 'r') as f:
            data = json.load(f)
            return data.get('skills', {})
    except FileNotFoundError:
        return {}

def load_spells_data():
    """Load spells from JSON file"""
    spells_file = os.path.join(basedir, 'data', 'spells', 'spells.json')
    try:
        with open(spells_file, 'r') as f:
            data = json.load(f)
            return data.get('spells', {})
    except FileNotFoundError:
        return {}

@app.route('/api/npcs')
def get_npcs():
    """Get all NPCs as JSON"""
    npcs = NPC.query.all()
    return jsonify([{
        'id': npc.id,
        'npc_id': npc.npc_id,
        'name': npc.name,
        'race': npc.race,
        'description': npc.description,
        'current_room_id': npc.current_room_id,
        'x': npc.x_coord,
        'y': npc.y_coord,
        'z': npc.z_coord,
        'attributes': npc.attributes,
        'max_hp': npc.max_hp,
        'current_hp': npc.current_hp,
        'max_mana': npc.max_mana,
        'current_mana': npc.current_mana,
        'max_movement': npc.max_movement,
        'current_movement': npc.current_movement,
        'trial_points': npc.trial_points,
        'progress_points': npc.progress_points,
        'gold': npc.gold,
        'silver': npc.silver,
        'copper': npc.copper,
        'avatar': npc.avatar,
        'skills': npc.skills or {},
        'spells': npc.spells or {},
        'ai_behavior': npc.ai_behavior,
        'is_hostile': npc.is_hostile,
        'respawn_time': npc.respawn_time,
        'loot_table': npc.loot_table or {},
        'dialogue': npc.dialogue or {},
        'faction': npc.faction,
        'reputation_required': npc.reputation_required,
        'is_unique': npc.is_unique
    } for npc in npcs])

@app.route('/api/npcs', methods=['POST'])
def create_npc():
    """Create a new NPC"""
    data = request.get_json()
    
    # Check for duplicate npc_id
    existing_npc = NPC.query.filter_by(npc_id=data['npc_id']).first()
    if existing_npc:
        return jsonify({'error': 'An NPC with this ID already exists'}), 400
    
    # Check for duplicate name
    existing_name = NPC.query.filter_by(name=data['name']).first()
    if existing_name:
        return jsonify({'error': 'An NPC with this name already exists'}), 400
    
    npc = NPC(
        npc_id=data['npc_id'],
        name=data['name'],
        race=data.get('race'),
        description=data.get('description', ''),
        current_room_id=data.get('current_room_id'),
        x_coord=data.get('x', 0),
        y_coord=data.get('y', 0),
        z_coord=data.get('z', 0),
        attributes=data.get('attributes', {}),
        max_hp=data.get('max_hp', 100),
        current_hp=data.get('current_hp', 100),
        max_mana=data.get('max_mana', 50),
        current_mana=data.get('current_mana', 50),
        max_movement=data.get('max_movement', 100),
        current_movement=data.get('current_movement', 100),
        trial_points=data.get('trial_points', 20),
        progress_points=data.get('progress_points', 0),
        gold=data.get('gold', 0),
        silver=data.get('silver', 0),
        copper=data.get('copper', 0),
        avatar=data.get('avatar'),
        skills=data.get('skills', {}),
        spells=data.get('spells', {}),
        ai_behavior=data.get('ai_behavior', 'passive'),
        is_hostile=data.get('is_hostile', False),
        respawn_time=data.get('respawn_time', 0),
        loot_table=data.get('loot_table', {}),
        dialogue=data.get('dialogue', {}),
        faction=data.get('faction'),
        reputation_required=data.get('reputation_required', 0),
        is_unique=data.get('is_unique', False)
    )
    
    # Initialize attributes if not provided
    if not npc.attributes:
        npc._init_default_attributes()
    
    # Calculate derived stats
    npc.calculate_derived_stats()
    
    db.session.add(npc)
    db.session.commit()
    
    return jsonify({
        'id': npc.id,
        'npc_id': npc.npc_id,
        'name': npc.name,
        'race': npc.race,
        'description': npc.description,
        'current_room_id': npc.current_room_id,
        'x': npc.x_coord,
        'y': npc.y_coord,
        'z': npc.z_coord,
        'attributes': npc.attributes,
        'max_hp': npc.max_hp,
        'current_hp': npc.current_hp,
        'max_mana': npc.max_mana,
        'current_mana': npc.current_mana,
        'max_movement': npc.max_movement,
        'current_movement': npc.current_movement,
        'trial_points': npc.trial_points,
        'progress_points': npc.progress_points,
        'gold': npc.gold,
        'silver': npc.silver,
        'copper': npc.copper,
        'avatar': npc.avatar,
        'skills': npc.skills or {},
        'spells': npc.spells or {},
        'ai_behavior': npc.ai_behavior,
        'is_hostile': npc.is_hostile,
        'respawn_time': npc.respawn_time,
        'loot_table': npc.loot_table or {},
        'dialogue': npc.dialogue or {},
        'faction': npc.faction,
        'reputation_required': npc.reputation_required,
        'is_unique': npc.is_unique
    })

@app.route('/api/npcs/<int:npc_id>', methods=['PUT'])
def update_npc(npc_id):
    """Update an existing NPC"""
    npc = NPC.query.get_or_404(npc_id)
    data = request.get_json()
    
    # Check for duplicate npc_id (excluding current NPC)
    if 'npc_id' in data and data['npc_id'] != npc.npc_id:
        existing_npc = NPC.query.filter_by(npc_id=data['npc_id']).filter(NPC.id != npc_id).first()
        if existing_npc:
            return jsonify({'error': 'An NPC with this ID already exists'}), 400
    
    # Check for duplicate name (excluding current NPC)
    if 'name' in data and data['name'] != npc.name:
        existing_name = NPC.query.filter_by(name=data['name']).filter(NPC.id != npc_id).first()
        if existing_name:
            return jsonify({'error': 'An NPC with this name already exists'}), 400
    
    # Update fields
    npc.npc_id = data.get('npc_id', npc.npc_id)
    npc.name = data.get('name', npc.name)
    npc.race = data.get('race', npc.race)
    npc.description = data.get('description', npc.description)
    npc.current_room_id = data.get('current_room_id', npc.current_room_id)
    npc.x_coord = data.get('x', npc.x_coord)
    npc.y_coord = data.get('y', npc.y_coord)
    npc.z_coord = data.get('z', npc.z_coord)
    npc.attributes = data.get('attributes', npc.attributes)
    npc.max_hp = data.get('max_hp', npc.max_hp)
    npc.current_hp = data.get('current_hp', npc.current_hp)
    npc.max_mana = data.get('max_mana', npc.max_mana)
    npc.current_mana = data.get('current_mana', npc.current_mana)
    npc.max_movement = data.get('max_movement', npc.max_movement)
    npc.current_movement = data.get('current_movement', npc.current_movement)
    npc.trial_points = data.get('trial_points', npc.trial_points)
    npc.progress_points = data.get('progress_points', npc.progress_points)
    npc.gold = data.get('gold', npc.gold)
    npc.silver = data.get('silver', npc.silver)
    npc.copper = data.get('copper', npc.copper)
    npc.avatar = data.get('avatar', npc.avatar)
    npc.skills = data.get('skills', npc.skills)
    npc.spells = data.get('spells', npc.spells)
    npc.ai_behavior = data.get('ai_behavior', npc.ai_behavior)
    npc.is_hostile = data.get('is_hostile', npc.is_hostile)
    npc.respawn_time = data.get('respawn_time', npc.respawn_time)
    npc.loot_table = data.get('loot_table', npc.loot_table)
    npc.dialogue = data.get('dialogue', npc.dialogue)
    npc.faction = data.get('faction', npc.faction)
    npc.reputation_required = data.get('reputation_required', npc.reputation_required)
    npc.is_unique = data.get('is_unique', npc.is_unique)
    
    # Recalculate derived stats if attributes changed
    if 'attributes' in data:
        npc.calculate_derived_stats()
    
    db.session.commit()
    
    return jsonify({
        'id': npc.id,
        'npc_id': npc.npc_id,
        'name': npc.name,
        'race': npc.race,
        'description': npc.description,
        'current_room_id': npc.current_room_id,
        'x': npc.x_coord,
        'y': npc.y_coord,
        'z': npc.z_coord,
        'attributes': npc.attributes,
        'max_hp': npc.max_hp,
        'current_hp': npc.current_hp,
        'max_mana': npc.max_mana,
        'current_mana': npc.current_mana,
        'max_movement': npc.max_movement,
        'current_movement': npc.current_movement,
        'trial_points': npc.trial_points,
        'progress_points': npc.progress_points,
        'gold': npc.gold,
        'silver': npc.silver,
        'copper': npc.copper,
        'avatar': npc.avatar,
        'skills': npc.skills or {},
        'spells': npc.spells or {},
        'ai_behavior': npc.ai_behavior,
        'is_hostile': npc.is_hostile,
        'respawn_time': npc.respawn_time,
        'loot_table': npc.loot_table or {},
        'dialogue': npc.dialogue or {},
        'faction': npc.faction,
        'reputation_required': npc.reputation_required,
        'is_unique': npc.is_unique
    })

@app.route('/api/npcs/<int:npc_id>', methods=['DELETE'])
def delete_npc(npc_id):
    """Delete an NPC"""
    npc = NPC.query.get_or_404(npc_id)
    
    # Delete the NPC
    db.session.delete(npc)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/rooms')
def get_rooms():
    """Get all rooms as JSON"""
    rooms = Room.query.all()
    return jsonify([{
        'id': room.id,
        'room_id': room.room_id,
        'name': room.name,
        'area_id': room.area_id,
        'x': room.x_coord,
        'y': room.y_coord,
        'z': room.z_coord
    } for room in rooms])

@app.route('/api/areas')
def get_areas():
    """Get all areas as JSON"""
    areas = Area.query.all()
    return jsonify([{
        'id': area.id,
        'area_id': area.area_id,
        'name': area.name
    } for area in areas])

@app.route('/api/avatars')
def get_avatars():
    """Get list of available avatar files"""
    avatars_dir = os.path.join(basedir, 'static', 'assets', 'avatars')
    try:
        avatar_files = [f for f in os.listdir(avatars_dir) if f.endswith('.png')]
        return jsonify(sorted(avatar_files))
    except FileNotFoundError:
        return jsonify([])

if __name__ == '__main__':
    # Run the NPC builder on port 5002
    app.run(debug=True, host='0.0.0.0', port=5002)

