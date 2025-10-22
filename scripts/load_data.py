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
    """Load item templates from JSON files"""
    item_files = [
        'data/items/weapons.json',
        'data/items/armor.json',
        'data/items/consumables.json',
        'data/items/containers.json',
        'data/items/crafting_materials.json',
        'data/items/gems.json',
        'data/items/keys.json',
        'data/items/magical_items.json',
        'data/items/misc_items.json',
        'data/items/tools.json',
        'data/items/clothing.json',
        'data/items/ammunition.json',
        'data/items/cooking_items.json',
        'data/items/furniture.json',
        'data/items/special_items.json',
        'data/items/recipes.json',
        'data/items/crafting_stations.json',
    ]
    
    total_loaded = 0
    
    for file_path in item_files:
        if not os.path.exists(file_path):
            print(f"Skipping {file_path} (not found)")
            continue
            
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Handle different JSON structures (some files have top-level keys, some don't)
            items_dict = data
            if isinstance(data, dict) and len(data) == 1:
                # If there's a wrapper key like 'item_templates', unwrap it
                first_key = list(data.keys())[0]
                if isinstance(data[first_key], dict):
                    items_dict = data[first_key]
            
            for template_data in items_dict.values():
                if not isinstance(template_data, dict):
                    continue
                    
                # Check if template already exists
                existing = ItemTemplate.query.filter_by(template_id=template_data['template_id']).first()
                if existing:
                    continue
                
                template = ItemTemplate(
                    template_id=template_data['template_id'],
                    name=template_data['name'],
                    description=template_data.get('description', ''),
                    item_type=template_data.get('item_type', 13),
                    base_type=template_data['base_type'],
                    subtype=template_data.get('subtype'),
                    weight=template_data.get('weight', 0.0),
                    value=template_data.get('value', 0),
                    quality_tier=template_data.get('quality_tier', 'common'),
                    material=template_data.get('material'),
                    item_flags=template_data.get('item_flags', []),
                    item_flags_2=template_data.get('item_flags_2', []),
                    wear_flags=template_data.get('wear_flags', []),
                    socket_count=template_data.get('socket_count', 0),
                    socket_types=template_data.get('socket_types', []),
                    weapon_type=template_data.get('weapon_type'),
                    weapon_flags=template_data.get('weapon_flags', []),
                    base_damage_min=template_data.get('base_damage_min'),
                    base_damage_max=template_data.get('base_damage_max'),
                    attack_speed=template_data.get('attack_speed', 1.0),
                    damage_types=template_data.get('damage_types', []),
                    armor_class=template_data.get('armor_class', 0),
                    armor_slot=template_data.get('armor_slot'),
                    damage_reduction=template_data.get('damage_reduction', {}),
                    container_capacity=template_data.get('container_capacity', 0),
                    container_weight_capacity=template_data.get('container_weight_capacity', 0.0),
                    weight_reduction=template_data.get('weight_reduction', 0.0),
                    consumable_charges=template_data.get('consumable_charges', 1),
                    consumable_effects=template_data.get('consumable_effects', []),
                    crafting_skill=template_data.get('crafting_skill'),
                    crafting_difficulty=template_data.get('crafting_difficulty', 1),
                    components_required=template_data.get('components_required', []),
                    disassembly_data=template_data.get('disassembly_data', {}),
                    equipment_stats=template_data.get('equipment_stats', {}),
                    requirements=template_data.get('requirements', {}),
                    max_durability=template_data.get('max_durability', 100),
                    max_enchantments=template_data.get('max_enchantments', 0),
                    enchantable=template_data.get('enchantable', True),
                    icon_path=template_data.get('icon_path')
                )
                db.session.add(template)
                total_loaded += 1
            
            print(f"Loaded {len(items_dict)} items from {os.path.basename(file_path)}")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    print(f"Total item templates loaded: {total_loaded}")

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
