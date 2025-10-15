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
    
    def get_characters_in_room(self):
        """Get all characters currently in this room"""
        return self.characters.all()
    
    def get_items_in_room(self):
        """Get all items currently in this room"""
        return self.room_items.all()
    
    def __repr__(self):
        return f'<Room {self.name} ({self.room_id})>'
