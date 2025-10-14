from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.character import Character
from app.models.room import Room
from app.models.chat_message import ChatMessage

game_bp = Blueprint('game', __name__)

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
        
        # Set starting location (we'll create this room later)
        starting_room = Room.query.filter_by(room_id='room_001').first()
        if starting_room:
            character.current_room_id = starting_room.id
        else:
            # If no starting room exists, create a basic one or leave current_room_id as None
            character.current_room_id = None
        
        db.session.add(character)
        db.session.commit()
        
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
