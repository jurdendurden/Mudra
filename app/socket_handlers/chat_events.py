from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from app import db
from app.models.character import Character

def register_chat_events(socketio):
    """Register chat-related socket events"""
    
    @socketio.on('join_chat')
    def handle_join_chat(data):
        """Join chat channels"""
        if not current_user.is_authenticated:
            emit('error', {'message': 'Authentication required'})
            return
        
        channel = data.get('channel', 'global')
        character = get_current_character()
        
        if not character:
            emit('error', {'message': 'No active character'})
            return
        
        # Join appropriate chat room
        if channel == 'global':
            join_room('chat_global')
        elif channel == 'local':
            if character.current_room:
                room_name = f"chat_room_{character.current_room.id}"
                join_room(room_name)
        elif channel == 'guild':
            # TODO: Implement guild system
            pass
        
        emit('chat_joined', {
            'channel': channel,
            'character_name': character.name
        })
    
    @socketio.on('chat_message')
    def handle_chat_message(data):
        """Handle chat message"""
        if not current_user.is_authenticated:
            emit('error', {'message': 'Authentication required'})
            return
        
        character = get_current_character()
        if not character:
            emit('error', {'message': 'No active character'})
            return
        
        message = data.get('message', '').strip()
        channel = data.get('channel', 'global')
        
        if not message:
            emit('error', {'message': 'Empty message'})
            return
        
        # Emit message to appropriate channel
        if channel == 'global':
            emit('chat_message', {
                'character_name': character.name,
                'message': message,
                'channel': 'global',
                'timestamp': get_timestamp()
            }, room='chat_global')
        elif channel == 'local':
            if character.current_room:
                room_name = f"chat_room_{character.current_room.id}"
                emit('chat_message', {
                    'character_name': character.name,
                    'message': message,
                    'channel': 'local',
                    'timestamp': get_timestamp()
                }, room=room_name)
        elif channel == 'whisper':
            target_name = data.get('target')
            if target_name:
                # TODO: Implement whisper system
                emit('chat_message', {
                    'character_name': character.name,
                    'message': message,
                    'channel': 'whisper',
                    'target': target_name,
                    'timestamp': get_timestamp()
                })
    
    @socketio.on('leave_chat')
    def handle_leave_chat(data):
        """Leave chat channels"""
        if not current_user.is_authenticated:
            return
        
        channel = data.get('channel', 'global')
        character = get_current_character()
        
        if not character:
            return
        
        # Leave appropriate chat room
        if channel == 'global':
            leave_room('chat_global')
        elif channel == 'local':
            if character.current_room:
                room_name = f"chat_room_{character.current_room.id}"
                leave_room(room_name)
        
        emit('chat_left', {'channel': channel})

def get_current_character():
    """Get the current user's active character (simplified for now)"""
    if not current_user.is_authenticated:
        return None
    
    # For now, return the first character
    # Later we'll implement character selection
    return current_user.characters.first()

def get_timestamp():
    """Get current timestamp for chat messages"""
    from datetime import datetime
    return datetime.utcnow().isoformat()
