#!/usr/bin/env python3
"""
Clean up orphaned rooms from the database.
This script removes rooms that aren't linked to any area.
"""

import sys
import os

# Add parent directory to path to import models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.room import Room, Area
from config import Config


def cleanup_orphaned_rooms(auto_confirm=False):
    """Remove rooms that aren't linked to any area"""
    app = create_app()
    
    with app.app_context():
        # Get all rooms without an area_id
        orphaned_rooms = Room.query.filter(
            (Room.area_id == None) | (Room.area_id == '')
        ).all()
        
        if not orphaned_rooms:
            print("No orphaned rooms found. Database is clean!")
            return
        
        print(f"\nFound {len(orphaned_rooms)} orphaned room(s) without area assignments:")
        print("="*80)
        
        for room in orphaned_rooms:
            print(f"  - {room.room_id}: {room.name} at ({room.x_coord}, {room.y_coord}, {room.z_coord})")
        
        print("="*80)
        
        if auto_confirm:
            response = 'yes'
            print(f"\nAuto-confirming deletion (--yes flag)")
        else:
            response = input(f"\nDelete these {len(orphaned_rooms)} room(s)? (yes/no): ")
        
        if response.lower() in ['yes', 'y']:
            # Store room_ids for exit cleanup
            deleted_room_ids = [room.room_id for room in orphaned_rooms]
            
            # Delete orphaned rooms
            for room in orphaned_rooms:
                db.session.delete(room)
            
            db.session.commit()
            print(f"\n[SUCCESS] Deleted {len(orphaned_rooms)} orphaned room(s)")
            
            # Clean up orphaned exits
            cleanup_orphaned_exits(deleted_room_ids)
        else:
            print("\nCleanup cancelled.")


def cleanup_orphaned_exits(deleted_room_ids):
    """Remove exits pointing to deleted rooms"""
    app = create_app()
    
    with app.app_context():
        all_rooms = Room.query.all()
        updated_count = 0
        
        for room in all_rooms:
            if not room.exits:
                continue
            
            exits_modified = False
            new_exits = dict(room.exits)
            
            # Remove any exits pointing to deleted rooms
            for direction, target_room_id in list(new_exits.items()):
                if target_room_id in deleted_room_ids:
                    del new_exits[direction]
                    exits_modified = True
            
            # Update room if exits were modified
            if exits_modified:
                room.exits = new_exits
                db.session.add(room)
                updated_count += 1
        
        if updated_count > 0:
            db.session.commit()
            print(f"[SUCCESS] Cleaned up orphaned exits in {updated_count} room(s)")
        else:
            print("[SUCCESS] No orphaned exits found")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean up orphaned rooms from database')
    parser.add_argument('--yes', '-y', action='store_true', help='Automatically confirm deletion')
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("MUDRA - Room Database Cleanup Utility")
    print("="*80)
    
    cleanup_orphaned_rooms(auto_confirm=args.yes)
    
    print("\n" + "="*80)
    print("Cleanup complete!")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()

