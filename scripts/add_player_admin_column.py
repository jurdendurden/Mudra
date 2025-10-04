#!/usr/bin/env python3
"""
Script to add admin column to players table
"""

import sqlite3
import os

def add_player_admin_column():
    """Add admin column to players table"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'mud_game.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(players)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_admin' in columns:
            print("Admin column already exists in players table")
            return True
        
        # Add the admin column
        cursor.execute("ALTER TABLE players ADD COLUMN is_admin BOOLEAN DEFAULT 0")
        
        # Set all existing players to False
        cursor.execute("UPDATE players SET is_admin = 0 WHERE is_admin IS NULL")
        
        conn.commit()
        conn.close()
        
        print("Successfully added admin column to players table")
        print("All existing players set to is_admin = False")
        return True
        
    except Exception as e:
        print(f"Error adding admin column: {e}")
        return False

if __name__ == '__main__':
    add_player_admin_column()
