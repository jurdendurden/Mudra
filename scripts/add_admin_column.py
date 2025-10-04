#!/usr/bin/env python3
"""
Script to add admin column to characters table
"""

import sqlite3
import os

def add_admin_column():
    """Add admin column to characters table"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'mud_game.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(characters)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_admin' in columns:
            print("Admin column already exists in characters table")
            return True
        
        # Add the admin column
        cursor.execute("ALTER TABLE characters ADD COLUMN is_admin BOOLEAN DEFAULT 0")
        
        # Set all existing characters to False
        cursor.execute("UPDATE characters SET is_admin = 0 WHERE is_admin IS NULL")
        
        conn.commit()
        conn.close()
        
        print("Successfully added admin column to characters table")
        print("All existing characters set to is_admin = False")
        return True
        
    except Exception as e:
        print(f"Error adding admin column: {e}")
        return False

if __name__ == '__main__':
    add_admin_column()
