#!/usr/bin/env python3
"""
Script to load initial game data into the database
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import Area, Room, ItemTemplate, Skill, Spell

def load_areas():
    """Load areas from JSON file"""
    with open('data/world/areas.json', 'r') as f:
        data = json.load(f)
    
    for area_data in data['areas'].values():
        area = Area(
            area_id=area_data['area_id'],
            name=area_data['name'],
            description=area_data['description'],
            level_range=area_data['level_range'],
            entry_requirements=area_data['entry_requirements'],
            environmental_effects=area_data['environmental_effects'],
            connected_areas=area_data['connected_areas']
        )
        db.session.add(area)
    
    print(f"Loaded {len(data['areas'])} areas")

def load_rooms():
    """Load rooms from JSON file"""
    with open('data/world/rooms.json', 'r') as f:
        data = json.load(f)
    
    for room_data in data['rooms'].values():
        # Find the area
        area = Area.query.filter_by(area_id=room_data['area_id']).first()
        if not area:
            print(f"Warning: Area {room_data['area_id']} not found for room {room_data['room_id']}")
            continue
        
        room = Room(
            room_id=room_data['room_id'],
            area_id=area.id,
            x_coord=room_data['x_coord'],
            y_coord=room_data['y_coord'],
            z_coord=room_data['z_coord'],
            name=room_data['name'],
            description=room_data['description'],
            short_description=room_data['short_description'],
            exits=room_data['exits'],
            items=room_data['items'],
            npcs=room_data['npcs'],
            lighting=room_data['lighting'],
            temperature=room_data['temperature'],
            weather_effects=room_data['weather_effects'],
            is_safe=room_data['is_safe'],
            is_indoors=room_data['is_indoors'],
            is_water=room_data['is_water'],
            is_air=room_data['is_air']
        )
        db.session.add(room)
    
    print(f"Loaded {len(data['rooms'])} rooms")

def load_item_templates():
    """Load item templates from JSON file"""
    with open('data/items/templates.json', 'r') as f:
        data = json.load(f)
    
    for template_data in data['item_templates'].values():
        template = ItemTemplate(
            template_id=template_data['template_id'],
            name=template_data['name'],
            description=template_data['description'],
            base_type=template_data['base_type'],
            subtype=template_data.get('subtype'),
            weight=template_data.get('weight', 0.0),
            value=template_data.get('value', 0),
            quality_tier=template_data.get('quality_tier', 'common'),
            components_required=template_data.get('components_required', []),
            disassembly_data=template_data.get('disassembly_data', {}),
            equipment_stats=template_data.get('equipment_stats', {}),
            requirements=template_data.get('requirements', {})
        )
        db.session.add(template)
    
    print(f"Loaded {len(data['item_templates'])} item templates")

def load_skills():
    """Load skills from JSON file"""
    with open('data/skills/skills.json', 'r') as f:
        data = json.load(f)
    
    for skill_data in data['skills'].values():
        skill = Skill(
            skill_id=skill_data['skill_id'],
            name=skill_data['name'],
            description=skill_data['description'],
            category=skill_data['category'],
            max_level=skill_data.get('max_level', 100),
            attribute_requirements=skill_data.get('attribute_requirements', {}),
            cost_formula=skill_data.get('cost_formula', 'level * 2'),
            governs=skill_data.get('governs', []),
            related_skills=skill_data.get('related_skills', {}),
            prerequisites=skill_data.get('prerequisites', []),
            unlock_conditions=skill_data.get('unlock_conditions', {})
        )
        db.session.add(skill)
    
    print(f"Loaded {len(data['skills'])} skills")

def load_spells():
    """Load spells from JSON file"""
    with open('data/spells/spells.json', 'r') as f:
        data = json.load(f)
    
    for spell_data in data['spells'].values():
        spell = Spell(
            spell_id=spell_data['spell_id'],
            name=spell_data['name'],
            description=spell_data['description'],
            school=spell_data['school'],
            mana_cost=spell_data.get('mana_cost', 10),
            cast_time=spell_data.get('cast_time', 1.0),
            cooldown=spell_data.get('cooldown', 0.0),
            range=spell_data.get('range', 1),
            attribute_requirements=spell_data.get('attribute_requirements', {}),
            skill_requirements=spell_data.get('skill_requirements', {}),
            progress_point_cost=spell_data.get('progress_point_cost', 5),
            effects=spell_data.get('effects', []),
            target_type=spell_data.get('target_type', 'self'),
            prerequisites=spell_data.get('prerequisites', []),
            unlock_conditions=spell_data.get('unlock_conditions', {})
        )
        db.session.add(spell)
    
    print(f"Loaded {len(data['spells'])} spells")

def main():
    """Load all game data"""
    app = create_app()
    
    with app.app_context():
        print("Loading game data...")
        
        # Load data in order (areas first, then rooms that reference them)
        load_areas()
        load_rooms()
        load_item_templates()
        load_skills()
        load_spells()
        
        # Commit all changes
        db.session.commit()
        
        print("Game data loaded successfully!")

if __name__ == "__main__":
    main()
