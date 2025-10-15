from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.character import Character
from app.models.room import Room
from app.models.chat_message import ChatMessage

game_bp = Blueprint('game', __name__)

def get_starting_village_location():
    """Get the starting village room and coordinates"""
    starting_room = Room.query.filter_by(room_id='room_001').first()
    if starting_room:
        return starting_room, starting_room.x_coord, starting_room.y_coord, starting_room.z_coord
    # Default fallback to (0, 0, 0) if room not found
    return None, 0, 0, 0

def validate_character_location(character):
    """Validate character location and reset to starting village if invalid"""
    # Check if character has coordinates
    if character.x_coord is None or character.y_coord is None or character.z_coord is None:
        # Set to starting village
        room, x, y, z = get_starting_village_location()
        character.x_coord = x
        character.y_coord = y
        character.z_coord = z
        if room:
            character.current_room_id = room.id
        db.session.commit()
        return True
    
    # Check if room exists at character's coordinates
    room = Room.query.filter_by(
        x_coord=character.x_coord,
        y_coord=character.y_coord,
        z_coord=character.z_coord
    ).first()
    
    if not room:
        # Room doesn't exist, move to starting village
        room, x, y, z = get_starting_village_location()
        character.x_coord = x
        character.y_coord = y
        character.z_coord = z
        if room:
            character.current_room_id = room.id
        db.session.commit()
        return True
    
    # Update current_room_id to match coordinates
    if character.current_room_id != room.id:
        character.current_room_id = room.id
        db.session.commit()
    
    return False

@game_bp.route('/')
@login_required
def index():
    """Account screen - character selection"""
    # Get user's characters
    characters = current_user.characters.all()
    
    # Calculate total hours played (simplified - using time since creation)
    from datetime import datetime
    total_hours = 0
    for char in characters:
        if char.last_played is not None and char.created_at is not None:
            time_diff = char.last_played - char.created_at
            total_hours += time_diff.total_seconds() / 3600
    
    return render_template('game/account.html', 
                         characters=characters, 
                         total_hours=total_hours)

@game_bp.route('/play/<int:character_id>')
@login_required
def play_character(character_id):
    """Load a specific character into the game"""
    character = Character.query.filter_by(
        id=character_id, 
        player_id=current_user.id
    ).first_or_404()
    
    print(f"[PLAY CHARACTER] Loading character {character.name} (ID: {character_id})")
    print(f"[PLAY CHARACTER] Initial coordinates: ({character.x_coord}, {character.y_coord}, {character.z_coord})")
    print(f"[PLAY CHARACTER] Current room ID: {character.current_room_id}")
    
    # Validate character location (will reset to starting village if invalid)
    was_reset = validate_character_location(character)
    if was_reset:
        flash('Your location was invalid and you have been moved to the Starting Village.', 'info')
        print(f"[PLAY CHARACTER] Character location was reset")
    
    print(f"[PLAY CHARACTER] Final coordinates: ({character.x_coord}, {character.y_coord}, {character.z_coord})")
    
    # Update last played timestamp
    from datetime import datetime
    character.last_played = datetime.utcnow()
    db.session.commit()
    
    return render_template('game/index.html', character=character)

@game_bp.route('/create-character', methods=['GET', 'POST'])
@login_required
def create_character():
    """Character creation"""
    if request.method == 'POST':
        name = request.form.get('name')
        race = request.form.get('race', 'Human')
        description = request.form.get('description', '')
        attributes_json = request.form.get('attributes')
        
        # Validation
        if not name:
            flash('Character name is required', 'error')
            return render_template('game/create_character.html')
        
        if not attributes_json:
            flash('Please distribute your trial points', 'error')
            return render_template('game/create_character.html')
        
        # Check if name is already taken
        if Character.query.filter_by(name=name).first():
            flash('Character name already exists', 'error')
            return render_template('game/create_character.html')
        
        try:
            # Parse attributes
            import json
            attributes = json.loads(attributes_json)
            
            # Validate that all points are used
            total_points_used = 0
            for prime_attr in attributes.values():
                for sub_attr_value in prime_attr.values():
                    total_points_used += sub_attr_value
            
            if total_points_used != 20:
                flash('You must use exactly 20 trial points', 'error')
                return render_template('game/create_character.html')
            
        except (json.JSONDecodeError, TypeError):
            flash('Invalid attribute data', 'error')
            return render_template('game/create_character.html')
        
        # Create new character
        character = Character(
            player_id=current_user.id,
            name=name,
            race=race,
            description=description,
            attributes=attributes,
            trial_points=0  # All points have been spent during creation
        )
        
        # Calculate derived stats based on attributes
        character.calculate_derived_stats()
        
        # Set starting location to Starting Village
        starting_room, x, y, z = get_starting_village_location()
        print(f"[CREATE CHARACTER] Starting village location: ({x}, {y}, {z}), room_id: {starting_room.id if starting_room else 'None'}")
        
        character.x_coord = x
        character.y_coord = y
        character.z_coord = z
        if starting_room:
            character.current_room_id = starting_room.id
        
        print(f"[CREATE CHARACTER] Character {name} created with coordinates: ({character.x_coord}, {character.y_coord}, {character.z_coord})")
        
        db.session.add(character)
        db.session.commit()
        
        print(f"[CREATE CHARACTER] Character {name} committed to database")
        
        # Verify the coordinates were saved
        db.session.refresh(character)
        print(f"[CREATE CHARACTER] Verified coordinates after commit: ({character.x_coord}, {character.y_coord}, {character.z_coord})")
        
        flash(f'Character {name} created successfully!', 'success')
        return redirect(url_for('game.index'))
    
    return render_template('game/create_character.html')

@game_bp.route('/delete-character/<int:character_id>', methods=['POST'])
@login_required
def delete_character(character_id):
    """Delete a character"""
    character = Character.query.filter_by(
        id=character_id, 
        player_id=current_user.id
    ).first_or_404()
    
    character_name = character.name
    db.session.delete(character)
    db.session.commit()
    
    flash(f'Character {character_name} has been deleted.', 'success')
    return redirect(url_for('game.index'))

@game_bp.route('/character/<int:character_id>')
@login_required
def character_sheet(character_id):
    """Character sheet view"""
    character = Character.query.filter_by(
        id=character_id, 
        player_id=current_user.id
    ).first_or_404()
    
    return render_template('game/character_sheet.html', character=character)

@game_bp.route('/api/character/<int:character_id>/attributes', methods=['POST'])
@login_required
def update_attributes(character_id):
    """Update character attributes via API"""
    character = Character.query.filter_by(
        id=character_id, 
        player_id=current_user.id
    ).first_or_404()
    
    data = request.get_json()
    prime_attr = data.get('prime_attr')
    sub_attr = data.get('sub_attr')
    value = data.get('value')
    
    if not all([prime_attr, sub_attr, value is not None]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate attribute unlock
    if not character.can_unlock_sub_attribute(prime_attr, sub_attr):
        return jsonify({'error': 'Cannot unlock this sub-attribute'}), 400
    
    # Calculate cost
    current_value = character.get_attribute_value(prime_attr, sub_attr)
    cost = int(value * 0.5)  # Simple cost formula
    
    if character.trial_points < cost:
        return jsonify({'error': 'Insufficient trial points'}), 400
    
    # Update attribute
    character.set_attribute_value(prime_attr, sub_attr, value)
    character.trial_points -= cost
    character.calculate_derived_stats()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'new_value': value,
        'remaining_points': character.trial_points
    })

@game_bp.route('/api/chat/recent', methods=['GET'])
@login_required
def get_recent_chat():
    """Get recent chat messages"""
    limit = request.args.get('limit', 50, type=int)
    
    # Get recent chat messages from chat database
    messages = ChatMessage.get_recent(limit)
    
    return jsonify({
        'success': True,
        'messages': messages
    })

@game_bp.route('/api/minimap/<int:character_id>', methods=['GET'])
@login_required
def get_minimap_data(character_id):
    """Get nearby rooms for minimap display"""
    # Expire all objects in session to force fresh data from database
    db.session.expire_all()
    
    character = Character.query.filter_by(
        id=character_id, 
        player_id=current_user.id
    ).first_or_404()
    
    print(f"[MINIMAP API] Getting minimap for character {character.name} (ID: {character_id})")
    print(f"[MINIMAP API] Character coordinates from DB: ({character.x_coord}, {character.y_coord}, {character.z_coord})")
    print(f"[MINIMAP API] Character current_room_id: {character.current_room_id}")
    
    # Get character's current position
    char_x = character.x_coord or 0
    char_y = character.y_coord or 0
    char_z = character.z_coord or 0
    
    print(f"[MINIMAP API] Using coordinates: ({char_x}, {char_y}, {char_z})")
    
    # Get nearby rooms (5 units in each direction)
    nearby_range = 5
    nearby_rooms = Room.query.filter(
        Room.x_coord.between(char_x - nearby_range, char_x + nearby_range),
        Room.y_coord.between(char_y - nearby_range, char_y + nearby_range),
        Room.z_coord == char_z
    ).all()
    
    print(f"[MINIMAP API] Found {len(nearby_rooms)} nearby rooms")
    
    # Format room data for minimap
    rooms_data = []
    for room in nearby_rooms:
        rooms_data.append({
            'id': room.id,
            'room_id': room.room_id,
            'name': room.name,
            'x': room.x_coord,
            'y': room.y_coord,
            'z': room.z_coord,
            'exits': room.exits or {}
        })
    
    response_data = {
        'success': True,
        'rooms': rooms_data,
        'player_position': {
            'x': char_x,
            'y': char_y,
            'z': char_z
        }
    }
    
    print(f"[MINIMAP API] Returning player position: ({char_x}, {char_y}, {char_z})")
    
    return jsonify(response_data)