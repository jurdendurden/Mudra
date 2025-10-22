from app import db
from datetime import datetime
import json

class Area(db.Model):
    """Game area/zone model"""
    __tablename__ = 'areas'
    
    id = db.Column(db.Integer, primary_key=True)
    area_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Area properties
    level_range = db.Column(db.JSON, default={'min': 1, 'max': 10})
    entry_requirements = db.Column(db.JSON, default=dict)
    environmental_effects = db.Column(db.JSON, default=list)
    climate = db.Column(db.String(20), default='temperate')  # arctic, cold, temperate, warm, tropical, desert
    
    # Connected areas
    connected_areas = db.Column(db.JSON, default=list)
    
    # Relationships
    rooms = db.relationship('Room', backref='area', lazy='dynamic')
    
    def __repr__(self):
        return f'<Area {self.name}>'

class Room(db.Model):
    """Individual room model"""
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'))
    
    # Location coordinates
    x_coord = db.Column(db.Integer, default=0)
    y_coord = db.Column(db.Integer, default=0)
    z_coord = db.Column(db.Integer, default=0)
    
    # Room properties
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    short_description = db.Column(db.String(500))
    
    # Exits (JSON format: {'north': 'room_002', 'south': 'room_003', ...})
    exits = db.Column(db.JSON, default=dict)
    
    # Doors (JSON format: {'north': {door_data}, 'south': {door_data}, ...})
    # Door data structure:
    # {
    #   'door_id': 'unique_door_id',
    #   'name': 'Heavy Oak Door',
    #   'description': 'A sturdy oak door with iron bindings',
    #   'key_id': 'item_template_id_for_key',  # Required if locked=True
    #   'lock_difficulty': 50,  # 0-255 (0-100 normal, 101-255 magical)
    #   'flags': ['closed', 'locked', 'pick_proof', 'pass_proof', 'secret', 'hidden', 'no_lock', 'no_knock', 'no_close']
    # }
    doors = db.Column(db.JSON, default=dict)
    
    # Room contents
    items = db.Column(db.JSON, default=list)  # Item template IDs that spawn here
    npcs = db.Column(db.JSON, default=list)   # NPC template IDs that spawn here
    
    # Environmental properties
    lighting = db.Column(db.String(20), default='normal')  # dark, dim, normal, bright
    weather_effects = db.Column(db.JSON, default=list)
    
    # Room flags
    is_safe = db.Column(db.Boolean, default=False)  # No PvP, no mobs
    is_indoors = db.Column(db.Boolean, default=True)
    is_water = db.Column(db.Boolean, default=False)
    is_air = db.Column(db.Boolean, default=False)
    
    # Relationships
    characters = db.relationship('Character', backref='current_room', lazy='dynamic')
    room_items = db.relationship('Item', backref='room', lazy='dynamic')
    
    def get_exit_room(self, direction):
        """Get the room ID for a given exit direction.
        First, try for an exact match. If not found, try for a key that startswith the direction (case-insensitive)."""
        dir_lower = direction.lower()
        # First, try exact match
        if dir_lower in self.exits:
            return self.exits[dir_lower]
        # Second, try startswith match
        for key in self.exits:
            if key.startswith(dir_lower):
                return self.exits[key], key
        return None
    
    def add_exit(self, direction, room_id):
        """Add an exit to another room"""
        self.exits[direction.lower()] = room_id
    
    def remove_exit(self, direction):
        """Remove an exit"""
        if direction.lower() in self.exits:
            del self.exits[direction.lower()]
    
    def get_available_exits(self):
        """Get list of available exit directions"""
        return list(self.exits.keys())
    
    def get_exit_description(self, direction):
        """Get description for an exit (can be enhanced later)"""
        exit_room_id = self.get_exit_room(direction)
        if exit_room_id:
            return f"To the {direction}"
        return None
    
    def has_door(self, direction):
        """Check if there's a door in a given direction"""
        return direction.lower() in (self.doors or {})
    
    def get_door(self, direction):
        """Get door data for a given direction"""
        if not self.doors:
            return None
        return self.doors.get(direction.lower())
    
    def add_door(self, direction, door_data):
        """Add or update a door in a given direction"""
        if not self.doors:
            self.doors = {}
        self.doors[direction.lower()] = door_data
        
        # Mark the field as modified for SQLAlchemy
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(self, 'doors')
    
    def remove_door(self, direction):
        """Remove a door from a given direction"""
        if self.doors and direction.lower() in self.doors:
            del self.doors[direction.lower()]
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(self, 'doors')
    
    def is_door_closed(self, direction):
        """Check if a door is closed"""
        door = self.get_door(direction)
        return door and 'closed' in door.get('flags', [])
    
    def is_door_locked(self, direction):
        """Check if a door is locked"""
        door = self.get_door(direction)
        return door and 'locked' in door.get('flags', [])
    
    def can_pass_door(self, direction, character=None, has_key=False):
        """Check if a character can pass through a door"""
        door = self.get_door(direction)
        if not door:
            return True, "No door"
        
        flags = door.get('flags', [])
        
        # Check pass_proof flag
        if 'pass_proof' in flags:
            return False, "The door is impassable"
        
        # Check if door is closed
        if 'closed' not in flags:
            return True, "Door is open"
        
        # Check if door is locked
        if 'locked' in flags:
            if has_key:
                return True, "Unlocked with key"
            return False, "The door is locked"
        
        return True, "Door is closed but not locked"
    
    def validate_door_data(self, door_data):
        """Validate door data structure and rules"""
        errors = []
        
        # Check required fields
        if not door_data.get('door_id'):
            errors.append("Door ID is required")
        
        if not door_data.get('name'):
            errors.append("Door name is required")
        
        # Check lock/key relationship
        flags = door_data.get('flags', [])
        if 'locked' in flags:
            if not door_data.get('key_id'):
                errors.append("Locked doors must have a key_id")
        
        # Check conflicting flags
        if 'no_lock' in flags and 'locked' in flags:
            errors.append("Door cannot have both 'no_lock' and 'locked' flags")
        
        if 'no_close' in flags and 'closed' in flags:
            errors.append("Door cannot have both 'no_close' and 'closed' flags")
        
        # Validate lock difficulty
        lock_difficulty = door_data.get('lock_difficulty', 0)
        if not isinstance(lock_difficulty, int) or lock_difficulty < 0 or lock_difficulty > 255:
            errors.append("Lock difficulty must be between 0 and 255")
        
        return len(errors) == 0, errors
    
    def get_characters_in_room(self):
        """Get all characters currently in this room"""
        return self.characters.all()
    
    def get_items_in_room(self):
        """Get all items currently in this room"""
        return self.room_items.all()
    
    def __repr__(self):
        return f'<Room {self.name} ({self.room_id})>'
