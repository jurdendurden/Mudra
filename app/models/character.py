from app import db
from datetime import datetime
import json
from app.utils.race_loader import (
    get_race_data, get_wearable_slots, get_racial_skill_bonuses,
    get_special_abilities, get_resistances, can_wear_slot
)

class Character(db.Model):
    """Character model with classless progression system"""
    __tablename__ = 'characters'
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    race = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_played = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Current location
    current_room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    x_coord = db.Column(db.Integer, default=0)
    y_coord = db.Column(db.Integer, default=0)
    z_coord = db.Column(db.Integer, default=0)
    
    # Attributes (JSON field for flexibility)
    attributes = db.Column(db.JSON, default=dict)
    
    # Derived stats
    max_hp = db.Column(db.Integer, default=100)
    current_hp = db.Column(db.Integer, default=100)
    max_mana = db.Column(db.Integer, default=50)
    current_mana = db.Column(db.Integer, default=50)
    max_movement = db.Column(db.Integer, default=100)
    current_movement = db.Column(db.Integer, default=100)
    
    # Progression points
    trial_points = db.Column(db.Integer, default=20)
    progress_points = db.Column(db.Integer, default=0)
    
    # Currency
    gold = db.Column(db.Integer, default=0)
    silver = db.Column(db.Integer, default=0)
    copper = db.Column(db.Integer, default=0)
    
    # Admin flag
    is_admin = db.Column(db.Boolean, default=False)
    
    # Skills and spells (JSON fields)
    skills = db.Column(db.JSON, default=dict)
    spells = db.Column(db.JSON, default=dict)
    
    # Relationships
    inventory = db.relationship('Item', backref='owner_character', lazy='dynamic', foreign_keys='Item.owner_character_id')
    equipped_items = db.relationship('Item', backref='equipped_character', lazy='dynamic', foreign_keys='Item.equipped_character_id')
    
    def get_attribute_value(self, prime_attr, sub_attr):
        """Get specific attribute value"""
        if not self.attributes:
            self._init_default_attributes()
        return self.attributes.get(prime_attr, {}).get(sub_attr, 0)
    
    def _init_default_attributes(self):
        """Initialize default attributes structure"""
        self.attributes = {
            'body': {'strength': 0, 'durability': 0, 'endurance': 0, 'vitality': 0},
            'mind': {'intellect': 0, 'cognition': 0, 'willpower': 0, 'psionics': 0},
            'spirit': {'mystical': 0, 'magical': 0, 'metaphysical': 0, 'percipience': 0},
            'kismet': {'luck': 0, 'charisma': 0}
        }
    
    def set_attribute_value(self, prime_attr, sub_attr, value):
        """Set specific attribute value"""
        if not self.attributes:
            self._init_default_attributes()
        if prime_attr not in self.attributes:
            self.attributes[prime_attr] = {}
        self.attributes[prime_attr][sub_attr] = value
    
    def get_total_attribute_points(self, prime_attr):
        """Get total points spent in a prime attribute"""
        if not self.attributes:
            self._init_default_attributes()
        return sum(self.attributes.get(prime_attr, {}).values())
    
    def can_unlock_sub_attribute(self, prime_attr, sub_attr):
        """Check if a sub-attribute can be unlocked"""
        if not self.attributes:
            self._init_default_attributes()
        current_sa = self.attributes.get(prime_attr, {})
        
        if sub_attr in current_sa:
            return True  # Already unlocked
        
        if prime_attr == 'kismet':
            # Kismet: 2nd SA at 10 points in first
            if len(current_sa) == 1:
                return sum(current_sa.values()) >= 10
        else:
            # Body/Mind/Spirit progression
            sa_count = len(current_sa)
            if sa_count == 0:
                return True  # First sub-attribute
            elif sa_count == 1:
                return sum(current_sa.values()) >= 5
            elif sa_count == 2:
                return sum(current_sa.values()) >= 15
            elif sa_count == 3:
                total_points = sum(current_sa.values())
                high_attrs = sum(1 for v in current_sa.values() if v >= 12)
                return total_points >= 30 and high_attrs >= 2
        
        return False
    
    def calculate_derived_stats(self):
        """Calculate HP, mana, and movement based on attributes"""
        # HP based on vitality and durability
        vitality = self.get_attribute_value('body', 'vitality')
        durability = self.get_attribute_value('body', 'durability')
        self.max_hp = 100 + (vitality * 5) + (durability * 3)
        
        # Mana based on mystical and magical
        mystical = self.get_attribute_value('spirit', 'mystical')
        magical = self.get_attribute_value('spirit', 'magical')
        self.max_mana = 50 + (mystical * 3) + (magical * 2)
        
        # Movement based on endurance
        endurance = self.get_attribute_value('body', 'endurance')
        self.max_movement = 100 + (endurance * 2)
        
        # Ensure current values don't exceed max
        if self.current_hp is None:
            self.current_hp = self.max_hp
        else:
            self.current_hp = min(self.current_hp, self.max_hp)
            
        if self.current_mana is None:
            self.current_mana = self.max_mana
        else:
            self.current_mana = min(self.current_mana, self.max_mana)
            
        if self.current_movement is None:
            self.current_movement = self.max_movement
        else:
            self.current_movement = min(self.current_movement, self.max_movement)
    
    def get_race_data(self):
        """Get full race data for this character"""
        if not self.race:
            return None
        return get_race_data(self.race)
    
    def get_wearable_slots(self):
        """Get available equipment slots for this character's race"""
        if not self.race:
            return []
        return get_wearable_slots(self.race)
    
    def can_wear_slot(self, slot_name):
        """Check if this character can wear items in a specific slot"""
        if not self.race:
            return True  # Default to allowing all slots
        return can_wear_slot(self.race, slot_name)
    
    def get_racial_skill_bonuses(self):
        """Get skill bonuses from race"""
        if not self.race:
            return {}
        return get_racial_skill_bonuses(self.race)
    
    def get_effective_skill_level(self, skill_name):
        """Get effective skill level including racial bonuses"""
        base_level = self.skills.get(skill_name, 0) if self.skills else 0
        racial_bonuses = self.get_racial_skill_bonuses()
        racial_bonus = racial_bonuses.get(skill_name, 0)
        return base_level + racial_bonus
    
    def get_special_abilities(self):
        """Get special abilities from race"""
        if not self.race:
            return []
        return get_special_abilities(self.race)
    
    def get_resistances(self):
        """Get damage/effect resistances from race"""
        if not self.race:
            return {}
        return get_resistances(self.race)
    
    def __repr__(self):
        return f'<Character {self.name}>'
