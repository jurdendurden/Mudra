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
    
    # Relationships
    characters = db.relationship('Character', backref='player', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def calculate_account_points(self):
        """Calculate account points based on achievements"""
        points = 0
        
        # Calculate total hours played across all characters
        total_hours = 0
        for char in self.characters:
            if char.last_played is not None and char.created_at is not None:
                time_diff = char.last_played - char.created_at
                total_hours += time_diff.total_seconds() / 3600
        
        # Hours played achievements (1 point per tier)
        hours_thresholds = [5, 10, 25, 100, 300, 1000, 2500, 5000]
        for threshold in hours_thresholds:
            if total_hours >= threshold:
                points += 1
        
        # Characters created achievements (1 point per tier)
        character_thresholds = [5, 10, 25, 50, 100, 250, 500]
        for threshold in character_thresholds:
            if len(self.characters.all()) >= threshold:
                points += 1
        
        return points
    
    def update_account_points(self):
        """Update account points based on current achievements"""
        self.account_points = self.calculate_account_points()
    
    def __repr__(self):
        return f'<Player {self.username}>'
