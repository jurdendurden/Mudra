#!/usr/bin/env python3
"""
Script to set a character as admin
Usage: python scripts/set_character_admin.py <character_name>
"""

import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.character import Character

def set_character_admin(character_name):
    """Set a character as admin"""
    app = create_app()
    
    with app.app_context():
        character = Character.query.filter_by(name=character_name).first()
        
        if not character:
            print(f"Character '{character_name}' not found!")
            return False
        
        character.is_admin = True
        db.session.commit()
        
        print(f"Character '{character_name}' is now an admin!")
        return True

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python scripts/set_character_admin.py <character_name>")
        sys.exit(1)
    
    character_name = sys.argv[1]
    set_character_admin(character_name)
