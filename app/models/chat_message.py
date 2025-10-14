from app.chat_db import chat_db
from datetime import datetime, timezone

class ChatMessage:
    """Chat message model for storing player communications"""
    
    def __init__(self, character_id, character_name, message):
        self.character_id = character_id
        self.character_name = character_name
        self.message = message
        self.timestamp = datetime.now(timezone.utc)
        self.id = None
    
    def save(self):
        """Save the chat message to the database"""
        self.id = chat_db.add_message(
            self.character_id,
            self.character_name,
            self.message
        )
        return self
    
    def to_dict(self):
        """Convert message to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'character_name': self.character_name,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'formatted_timestamp': self.timestamp.strftime('%H:%M:%S')
        }
    
    @staticmethod
    def get_recent(limit=50):
        """Get recent chat messages"""
        return chat_db.get_recent_messages(limit)
    
    def __repr__(self):
        return f'<ChatMessage {self.id}: {self.character_name}: {self.message[:50]}...>'
