#!/usr/bin/env python3
"""
Coordinate validation utility for the MUD room system.
This script validates room coordinates to ensure no overlaps and proper exit connections.
"""

import sys
import os
import json
from collections import defaultdict

# Add parent directory to path to import models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.room import Room, Area
from config import Config


def validate_coordinates_from_db():
    """Validate coordinates from the database"""
    app = create_app()
    
    with app.app_context():
        rooms = Room.query.all()
        return validate_room_coordinates(rooms)


def validate_coordinates_from_json(json_file):
    """Validate coordinates from a JSON file"""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    rooms = []
    for room_id, room_data in data.get('rooms', {}).items():
        rooms.append({
            'room_id': room_data['room_id'],
            'name': room_data['name'],
            'x_coord': room_data.get('x_coord', 0),
            'y_coord': room_data.get('y_coord', 0),
            'z_coord': room_data.get('z_coord', 0),
            'exits': room_data.get('exits', {})
        })
    
    return validate_room_coordinates(rooms)


def validate_room_coordinates(rooms):
    """
    Validate room coordinates for overlaps and exit consistency.
    
    Args:
        rooms: List of room objects or dictionaries with coordinate information
    
    Returns:
        dict: Validation results with errors and warnings
    """
    results = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'statistics': {
            'total_rooms': 0,
            'coordinate_ranges': {
                'x_min': 0, 'x_max': 0,
                'y_min': 0, 'y_max': 0,
                'z_min': 0, 'z_max': 0
            }
        }
    }
    
    # Build coordinate map
    coord_map = {}
    exit_map = defaultdict(dict)
    
    for room in rooms:
        results['statistics']['total_rooms'] += 1
        
        # Get coordinates
        if hasattr(room, 'x_coord'):
            x, y, z = room.x_coord, room.y_coord, room.z_coord
            room_id = room.room_id
            name = room.name
            exits = room.exits or {}
        else:
            x, y, z = room['x_coord'], room['y_coord'], room['z_coord']
            room_id = room['room_id']
            name = room['name']
            exits = room.get('exits', {})
        
        # Update coordinate ranges
        results['statistics']['coordinate_ranges']['x_min'] = min(results['statistics']['coordinate_ranges']['x_min'], x)
        results['statistics']['coordinate_ranges']['x_max'] = max(results['statistics']['coordinate_ranges']['x_max'], x)
        results['statistics']['coordinate_ranges']['y_min'] = min(results['statistics']['coordinate_ranges']['y_min'], y)
        results['statistics']['coordinate_ranges']['y_max'] = max(results['statistics']['coordinate_ranges']['y_max'], y)
        results['statistics']['coordinate_ranges']['z_min'] = min(results['statistics']['coordinate_ranges']['z_min'], z)
        results['statistics']['coordinate_ranges']['z_max'] = max(results['statistics']['coordinate_ranges']['z_max'], z)
        
        # Check for overlaps
        coord = (x, y, z)
        if coord in coord_map:
            error_msg = f"OVERLAP: Room '{name}' ({room_id}) at ({x}, {y}, {z}) overlaps with '{coord_map[coord]['name']}' ({coord_map[coord]['room_id']})"
            results['errors'].append(error_msg)
            results['valid'] = False
        else:
            coord_map[coord] = {'room_id': room_id, 'name': name}
        
        # Store exits for validation
        exit_map[room_id] = exits
    
    # Validate exit connections
    direction_offsets = {
        'north': (0, 1, 0),
        'south': (0, -1, 0),
        'east': (1, 0, 0),
        'west': (-1, 0, 0),
        'up': (0, 0, 1),
        'down': (0, 0, -1)
    }
    
    for room in rooms:
        if hasattr(room, 'x_coord'):
            x, y, z = room.x_coord, room.y_coord, room.z_coord
            room_id = room.room_id
            name = room.name
            exits = room.exits or {}
        else:
            x, y, z = room['x_coord'], room['y_coord'], room['z_coord']
            room_id = room['room_id']
            name = room['name']
            exits = room.get('exits', {})
        
        for direction, target_room_id in exits.items():
            if not target_room_id:
                continue
            
            # Check if exit direction is valid
            if direction not in direction_offsets:
                error_msg = f"INVALID EXIT: Room '{name}' ({room_id}) has invalid exit direction '{direction}'"
                results['errors'].append(error_msg)
                results['valid'] = False
                continue
            
            # Find target room coordinates
            target_room = None
            for r in rooms:
                if (hasattr(r, 'room_id') and r.room_id == target_room_id) or (isinstance(r, dict) and r['room_id'] == target_room_id):
                    target_room = r
                    break
            
            if not target_room:
                warning_msg = f"WARNING: Room '{name}' ({room_id}) has exit '{direction}' to non-existent room '{target_room_id}'"
                results['warnings'].append(warning_msg)
                continue
            
            # Get target coordinates
            if hasattr(target_room, 'x_coord'):
                tx, ty, tz = target_room.x_coord, target_room.y_coord, target_room.z_coord
            else:
                tx, ty, tz = target_room['x_coord'], target_room['y_coord'], target_room['z_coord']
            
            # Calculate expected coordinates based on direction
            dx, dy, dz = direction_offsets[direction]
            expected_x = x + dx
            expected_y = y + dy
            expected_z = z + dz
            
            # Check if coordinates match expected
            if (tx, ty, tz) != (expected_x, expected_y, expected_z):
                warning_msg = f"WARNING: Room '{name}' ({room_id}) at ({x}, {y}, {z}) has exit '{direction}' to '{target_room_id}' at ({tx}, {ty}, {tz}), but expected ({expected_x}, {expected_y}, {expected_z})"
                results['warnings'].append(warning_msg)
    
    return results


def print_validation_results(results):
    """Print validation results in a readable format"""
    print("\n" + "="*80)
    print("COORDINATE VALIDATION RESULTS")
    print("="*80)
    
    stats = results['statistics']
    print(f"\nTotal Rooms: {stats['total_rooms']}")
    print(f"\nCoordinate Ranges:")
    print(f"  X: {stats['coordinate_ranges']['x_min']} to {stats['coordinate_ranges']['x_max']}")
    print(f"  Y: {stats['coordinate_ranges']['y_min']} to {stats['coordinate_ranges']['y_max']}")
    print(f"  Z: {stats['coordinate_ranges']['z_min']} to {stats['coordinate_ranges']['z_max']}")
    
    if results['errors']:
        print(f"\n{'='*80}")
        print(f"ERRORS ({len(results['errors'])})")
        print("="*80)
        for error in results['errors']:
            print(f"  [ERROR] {error}")
    
    if results['warnings']:
        print(f"\n{'='*80}")
        print(f"WARNINGS ({len(results['warnings'])})")
        print("="*80)
        for warning in results['warnings']:
            print(f"  [WARN] {warning}")
    
    print(f"\n{'='*80}")
    if results['valid']:
        print("[SUCCESS] VALIDATION PASSED: No coordinate overlaps found!")
    else:
        print("[FAILED] VALIDATION FAILED: Please fix the errors above.")
    print("="*80 + "\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate room coordinates in the MUD system')
    parser.add_argument('--json', type=str, help='Path to JSON file to validate (default: validate database)')
    parser.add_argument('--fix', action='store_true', help='Attempt to auto-fix coordinate issues (not implemented yet)')
    
    args = parser.parse_args()
    
    if args.json:
        print(f"Validating coordinates from JSON file: {args.json}")
        results = validate_coordinates_from_json(args.json)
    else:
        print("Validating coordinates from database...")
        results = validate_coordinates_from_db()
    
    print_validation_results(results)
    
    # Exit with error code if validation failed
    sys.exit(0 if results['valid'] else 1)


if __name__ == '__main__':
    main()

