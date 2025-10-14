from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from app import db
from app.models.character import Character
from app.models.room import Room
from app.systems.commands import CommandProcessor

def register_game_events(socketio):
    """Register game-related socket events"""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        if current_user.is_authenticated:
            emit('connected', {'message': 'Connected to game server'})
        else:
            emit('error', {'message': 'Authentication required'})
            return False
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        if current_user.is_authenticated:
            # Leave all rooms
            character = get_current_character()
            if character and character.current_room:
                leave_room(f"room_{character.current_room.id}")
    
    @socketio.on('join_game')
    def handle_join_game(data):
        """Join the game with a character"""
        if not current_user.is_authenticated:
            emit('error', {'message': 'Authentication required'})
            return
        
        character_id = data.get('character_id')
        if not character_id:
            emit('error', {'message': 'Character ID required'})
            return
        
        character = Character.query.filter_by(
            id=character_id, 
            player_id=current_user.id
        ).first()
        
        if not character:
            emit('error', {'message': 'Character not found'})
            return
        
        # Join character's current room
        if character.current_room:
            room_name = f"room_{character.current_room.id}"
            join_room(room_name)
            emit('joined_room', {
                'room_id': character.current_room.id,
                'room_name': character.current_room.name
            })
        
        emit('game_joined', {
            'character_id': character.id,
            'character_name': character.name
        })
    
    @socketio.on('game_command')
    def handle_game_command(data):
        """Process game command"""
        if not current_user.is_authenticated:
            emit('error', {'message': 'Authentication required'})
            return
        
        command = data.get('command', '').strip()
        if not command:
            emit('error', {'message': 'Empty command'})
            return
        
        character = get_current_character()
        if not character:
            emit('error', {'message': 'No active character'})
            return
        
        # Process command
        processor = CommandProcessor()
        result = processor.process_command(character, command)
        
        # Emit result to client
        emit('command_result', {
            'command': command,
            'result': result
        })
        
        # If command affected room state, notify other players in room
        if character.current_room and result.get('affects_room'):
            room_name = f"room_{character.current_room.id}"
            emit('room_update', {
                'character_id': character.id,
                'character_name': character.name,
                'action': result.get('action'),
                'message': result.get('room_message')
            }, room=room_name, include_self=False)
        
        # If command was chat, emit chat message to all players
        if result.get('action') == 'chat' and result.get('chat_message'):
            # Add player's censor preference to the message
            chat_data = result['chat_message'].copy()
            chat_data['player_censor_enabled'] = character.player.censor_enabled
            emit('chat_message', chat_data, broadcast=True)
    
    @socketio.on('request_room_info')
    def handle_request_room_info():
        """Request current room information"""
        if not current_user.is_authenticated:
            emit('error', {'message': 'Authentication required'})
            return
        
        character = get_current_character()
        if not character or not character.current_room:
            emit('error', {'message': 'Not in a room'})
            return
        
        room = character.current_room
        
        # Get other characters in room
        other_characters = []
        for char in room.get_characters_in_room():
            if char.id != character.id:
                other_characters.append({
                    'id': char.id,
                    'name': char.name,
                    'description': char.description
                })
        
        # Get items in room
        room_items = []
        for item in room.get_items_in_room():
            room_items.append({
                'id': item.id,
                'name': item.name,
                'description': item.description
            })
        
        emit('room_info', {
            'room': {
                'id': room.id,
                'name': room.name,
                'description': room.description,
                'exits': room.get_available_exits(),
                'lighting': room.lighting,
                'is_safe': room.is_safe
            },
            'characters': other_characters,
            'items': room_items
        })

def get_current_character():
    """Get the current user's active character (simplified for now)"""
    if not current_user.is_authenticated:
        return None
    
    # For now, return the first character
    # Later we'll implement character selection
    return current_user.characters.first()
