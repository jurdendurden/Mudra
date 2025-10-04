#!/usr/bin/env python3
"""
Script to set a player as admin
Usage: python scripts/set_admin.py <username>
"""

import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.player import Player

def set_admin(username):
    """Set a player as admin"""
    app = create_app()
    
    with app.app_context():
        player = Player.query.filter_by(username=username).first()
        
        if not player:
            print(f"Player '{username}' not found!")
            return False
        
        player.is_admin = True
        db.session.commit()
        
        print(f"Player '{username}' is now an admin!")
        return True

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python scripts/set_admin.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    set_admin(username)
