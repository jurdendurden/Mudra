#!/usr/bin/env python3
"""
Script to fix character coordinates for all existing characters.
Sets characters without valid coordinates to Starting Village (0, 0, 0).
"""

import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.character import Character
from app.models.room import Room

def fix_character_coordinates():
    """Fix coordinates for all characters"""
    app = create_app()
    
    with app.app_context():
        # Get the starting village room
        starting_room = Room.query.filter_by(room_id='room_001').first()
        
        if not starting_room:
            print("ERROR: Starting room (room_001) not found in database!")
            print("Please load the rooms data first.")
            return False
        
        print(f"Starting Village found at coordinates ({starting_room.x_coord}, {starting_room.y_coord}, {starting_room.z_coord})")
        print()
        
        # Get all characters
        characters = Character.query.all()
        
        if not characters:
            print("No characters found in database.")
            return True
        
        print(f"Found {len(characters)} character(s) to check...")
        print()
        
        fixed_count = 0
        already_valid_count = 0
        
        for character in characters:
            # Check if character has invalid coordinates
            needs_fix = False
            
            if character.x_coord is None or character.y_coord is None or character.z_coord is None:
                needs_fix = True
                reason = "missing coordinates"
            else:
                # Check if room exists at character's coordinates
                room = Room.query.filter_by(
                    x_coord=character.x_coord,
                    y_coord=character.y_coord,
                    z_coord=character.z_coord
                ).first()
                
                if not room:
                    needs_fix = True
                    reason = f"invalid coordinates ({character.x_coord}, {character.y_coord}, {character.z_coord})"
                else:
                    # Coordinates are valid, just ensure current_room_id matches
                    if character.current_room_id != room.id:
                        character.current_room_id = room.id
                        print(f"  - {character.name}: Updated room_id to match coordinates")
            
            if needs_fix:
                print(f"  - {character.name}: {reason}")
                print(f"    Moving to Starting Village ({starting_room.x_coord}, {starting_room.y_coord}, {starting_room.z_coord})")
                
                character.x_coord = starting_room.x_coord
                character.y_coord = starting_room.y_coord
                character.z_coord = starting_room.z_coord
                character.current_room_id = starting_room.id
                
                fixed_count += 1
            else:
                already_valid_count += 1
        
        # Commit all changes
        db.session.commit()
        
        print()
        print("=" * 60)
        print(f"Summary:")
        print(f"  - Characters with valid coordinates: {already_valid_count}")
        print(f"  - Characters fixed: {fixed_count}")
        print(f"  - Total characters: {len(characters)}")
        print("=" * 60)
        print()
        print("All character coordinates have been validated and fixed!")
        
        return True

if __name__ == '__main__':
    success = fix_character_coordinates()
    sys.exit(0 if success else 1)

