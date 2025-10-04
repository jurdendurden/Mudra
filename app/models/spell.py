from app import db
from datetime import datetime
import json

class Spell(db.Model):
    """Spell template model"""
    __tablename__ = 'spells'
    
    id = db.Column(db.Integer, primary_key=True)
    spell_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    school = db.Column(db.String(50), nullable=False)  # mystical, magical, psionics
    
    # Spell properties
    mana_cost = db.Column(db.Integer, default=10)
    cast_time = db.Column(db.Float, default=1.0)  # seconds
    cooldown = db.Column(db.Float, default=0.0)  # seconds
    range = db.Column(db.Integer, default=1)  # room distance
    
    # Requirements
    attribute_requirements = db.Column(db.JSON, default=dict)
    skill_requirements = db.Column(db.JSON, default=dict)
    progress_point_cost = db.Column(db.Integer, default=5)
    
    # Spell effects
    effects = db.Column(db.JSON, default=list)
    target_type = db.Column(db.String(20), default='self')  # self, target, area, room
    
    # Learning requirements
    prerequisites = db.Column(db.JSON, default=list)
    unlock_conditions = db.Column(db.JSON, default=dict)
    
    def can_learn(self, character):
        """Check if character can learn this spell"""
        # Check attribute requirements
        for attr_category, requirements in self.attribute_requirements.items():
            for sub_attr, min_value in requirements.items():
                if character.get_attribute_value(attr_category, sub_attr) < min_value:
                    return False, f"Requires {attr_category}.{sub_attr} >= {min_value}"
        
        # Check skill requirements
        for skill_name, min_level in self.skill_requirements.items():
            if character.skills.get(skill_name, 0) < min_level:
                return False, f"Requires {skill_name} level {min_level}"
        
        # Check prerequisites
        for prereq in self.prerequisites:
            prereq_spell = prereq.get('spell')
            if prereq_spell not in character.spells:
                return False, f"Requires spell: {prereq_spell}"
        
        return True, "Can learn"
    
    def calculate_mana_cost(self, caster_level=0, caster_attributes=None):
        """Calculate actual mana cost based on caster's level and attributes"""
        base_cost = self.mana_cost
        
        # Reduce cost based on relevant attributes
        if caster_attributes:
            if self.school == 'mystical':
                mystical = caster_attributes.get('spirit', {}).get('mystical', 0)
                cost_reduction = mystical * 0.1
            elif self.school == 'magical':
                magical = caster_attributes.get('spirit', {}).get('magical', 0)
                cost_reduction = magical * 0.1
            elif self.school == 'psionics':
                psionics = caster_attributes.get('mind', {}).get('psionics', 0)
                cost_reduction = psionics * 0.1
            else:
                cost_reduction = 0
            
            base_cost = max(1, int(base_cost - cost_reduction))
        
        return base_cost
    
    def __repr__(self):
        return f'<Spell {self.name}>'

class CharacterSpell(db.Model):
    """Character's known spells"""
    __tablename__ = 'character_spells'
    
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    spell_id = db.Column(db.Integer, db.ForeignKey('spells.id'), nullable=False)
    
    # Spell progression
    level = db.Column(db.Integer, default=1)
    experience = db.Column(db.Integer, default=0)
    
    # Usage tracking
    times_cast = db.Column(db.Integer, default=0)
    last_cast = db.Column(db.DateTime)
    
    # Metadata
    learned_at = db.Column(db.DateTime, default=datetime.utcnow)
    learned_from = db.Column(db.String(100))  # scroll, teacher, discovery
    
    # Relationships
    character = db.relationship('Character', backref='character_spells')
    spell = db.relationship('Spell', backref='character_spells')
    
    def gain_experience(self, amount):
        """Gain experience in this spell"""
        self.experience += amount
        
        # Check for level up (spells level up more slowly)
        experience_needed = 100 * (self.level ** 1.5)
        if self.experience >= experience_needed:
            self.experience -= experience_needed
            self.level += 1
    
    def __repr__(self):
        return f'<CharacterSpell {self.character.name} - {self.spell.name} (Lv.{self.level})>'
