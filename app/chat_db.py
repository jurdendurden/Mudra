"""
Separate database module for chat messages

Run this script to initialize the chat database.
DCH 10/14/2025
"""
import sqlite3
import os
from datetime import datetime, timezone

class ChatDatabase:
    """Simple SQLite database for chat messages"""
    
    def __init__(self, db_path='instance/chat_logs.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the chat database with tables"""
        # Ensure the instance directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create chat_messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id INTEGER NOT NULL,
                character_name TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_message(self, character_id, character_name, message):
        """Add a chat message to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_messages (character_id, character_name, message, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (character_id, character_name, message, datetime.now(timezone.utc)))
        
        conn.commit()
        message_id = cursor.lastrowid
        conn.close()
        
        return message_id
    
    def get_recent_messages(self, limit=50):
        """Get recent chat messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, character_id, character_name, message, timestamp
            FROM chat_messages
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'id': row[0],
                'character_id': row[1],
                'character_name': row[2],
                'message': row[3],
                'timestamp': row[4],
                'formatted_timestamp': datetime.fromisoformat(row[4]).strftime('%H:%M:%S')
            })
        
        conn.close()
        return list(reversed(messages))  # Return oldest first
    
    def get_message_count(self):
        """Get total number of chat messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM chat_messages')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count

# Global instance
chat_db = ChatDatabase()
