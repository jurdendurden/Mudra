from app import db
from datetime import datetime
import json

class Skill(db.Model):
    """Skill template model"""
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)  # combat, crafting, utility, magic, social
    
    # Skill properties
    max_level = db.Column(db.Integer, default=100)
    attribute_requirements = db.Column(db.JSON, default=dict)
    cost_formula = db.Column(db.String(100), default='level * 2')  # Progress points cost
    
    # Skill relationships and bonuses
    governs = db.Column(db.JSON, default=list)  # What this skill affects
    related_skills = db.Column(db.JSON, default=dict)  # Bonuses/penalties with other skills
    
    # Learning requirements
    prerequisites = db.Column(db.JSON, default=list)  # Other skills required
    unlock_conditions = db.Column(db.JSON, default=dict)
    
    def calculate_cost(self, current_level):
        """Calculate progress point cost to advance to next level"""
        # Simple formula: level * 2 (can be made more complex)
        return current_level * 2
    
    def can_learn(self, character):
        """Check if character can learn this skill"""
        # Check attribute requirements
        for attr_category, requirements in self.attribute_requirements.items():
            for sub_attr, min_value in requirements.items():
                if character.get_attribute_value(attr_category, sub_attr) < min_value:
                    return False, f"Requires {attr_category}.{sub_attr} >= {min_value}"
        
        # Check prerequisites
        for prereq in self.prerequisites:
            prereq_skill = prereq.get('skill')
            prereq_level = prereq.get('level', 1)
            if character.skills.get(prereq_skill, 0) < prereq_level:
                return False, f"Requires {prereq_skill} level {prereq_level}"
        
        return True, "Can learn"
    
    def __repr__(self):
        return f'<Skill {self.name}>'

class CharacterSkill(db.Model):
    """Character's skill progression"""
    __tablename__ = 'character_skills'
    
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    
    # Skill progression
    level = db.Column(db.Integer, default=0)
    experience = db.Column(db.Integer, default=0)
    experience_to_next = db.Column(db.Integer, default=100)
    
    # Metadata
    learned_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    
    # Relationships
    character = db.relationship('Character', backref='character_skills')
    skill = db.relationship('Skill', backref='character_skills')
    
    def gain_experience(self, amount):
        """Gain experience in this skill"""
        self.experience += amount
        
        # Check for level up
        while self.experience >= self.experience_to_next and self.level < self.skill.max_level:
            self.experience -= self.experience_to_next
            self.level += 1
            self.experience_to_next = self.calculate_next_level_cost()
    
    def calculate_next_level_cost(self):
        """Calculate experience needed for next level"""
        # Simple formula: base * (level + 1)
        return 100 * (self.level + 1)
    
    def __repr__(self):
        return f'<CharacterSkill {self.character.name} - {self.skill.name} (Lv.{self.level})>'
