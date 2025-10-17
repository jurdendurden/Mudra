from app import db
from flask_login import UserMixin
from datetime import datetime
import bcrypt

class Player(UserMixin, db.Model):
    """Player account model"""
    __tablename__ = 'players'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    censor_enabled = db.Column(db.Boolean, default=True)
    account_points = db.Column(db.Integer, default=0)
    character_slots = db.Column(db.Integer, default=3)
    
    # Relationships
    characters = db.relationship('Character', backref='player', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def calculate_account_points(self):
        """Calculate account points based on achievements (triangular progression)"""
        points = 0
        
        # Calculate total hours played across all characters
        total_hours = 0
        for char in self.characters:
            if char.last_played is not None and char.created_at is not None:
                time_diff = char.last_played - char.created_at
                total_hours += time_diff.total_seconds() / 3600
        
        # Hours played achievements (triangular progression - tier number = points)
        hours_thresholds = [5, 10, 25, 100, 300, 1000, 2500, 5000]
        for i, threshold in enumerate(hours_thresholds, 1):
            if total_hours >= threshold:
                points += i
        
        # Characters created achievements (triangular progression - tier number = points)
        character_thresholds = [5, 10, 25, 50, 100, 250, 500]
        for i, threshold in enumerate(character_thresholds, 1):
            if len(self.characters.all()) >= threshold:
                points += i
        
        return points
    
    def update_account_points(self):
        """Update account points based on current achievements"""
        self.account_points = self.calculate_account_points()
    
    def get_max_characters(self):
        """Get maximum number of characters this player can have"""
        if self.is_admin:
            return 20  # Admins get max slots
        return self.character_slots or 3  # Default to 3 if None
    
    def can_create_character(self):
        """Check if player can create another character"""
        return len(self.characters.all()) < self.get_max_characters()
    
    def get_next_slot_cost(self):
        """Get cost for next character slot purchase"""
        current_slots = self.character_slots or 3  # Default to 3 if None
        if current_slots >= 20:  # Max slots reached
            return None
        
        # First purchasable slot (slot 4) costs 10, then 10 more each time
        # Slot 4 costs 10, slot 5 costs 20, slot 6 costs 30, etc.
        if current_slots <= 3:  # Only slots 4+ are purchasable
            return None
        
        # Slot 4 is the first purchasable slot, so it's purchase #1
        # Slot 5 is purchase #2, etc.
        purchase_number = current_slots - 3
        return 10 * purchase_number
    
    def purchase_character_slot(self):
        """Purchase an additional character slot"""
        current_slots = self.character_slots or 3  # Default to 3 if None
        if current_slots >= 20:
            return False, "Maximum character slots reached"
        
        cost = self.get_next_slot_cost()
        if cost is None:
            return False, "Maximum character slots reached"
        
        if self.account_points < cost:
            return False, f"Insufficient account points. Need {cost}, have {self.account_points}"
        
        self.account_points -= cost
        self.character_slots = current_slots + 1
        return True, f"Character slot purchased for {cost} points"
    
    def __repr__(self):
        return f'<Player {self.username}>'
