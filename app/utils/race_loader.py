"""
Race data loader and utilities for the race system.
Loads race JSON files and provides helper functions for racial bonuses.
"""

import json
import os
from pathlib import Path


class RaceLoader:
    """Singleton class to load and cache race data"""
    
    _instance = None
    _races = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RaceLoader, cls).__new__(cls)
            cls._instance._load_races()
        return cls._instance
    
    def _load_races(self):
        """Load all race JSON files from data/races/"""
        races_dir = Path(__file__).parent.parent.parent / 'data' / 'races'
        
        if not races_dir.exists():
            print(f"Warning: Races directory not found: {races_dir}")
            return
        
        for race_file in races_dir.glob('*.json'):
            try:
                with open(race_file, 'r', encoding='utf-8') as f:
                    race_data = json.load(f)
                    race_name = race_data.get('name', race_file.stem.title())
                    self._races[race_name] = race_data
            except Exception as e:
                print(f"Error loading race file {race_file}: {e}")
    
    def get_race(self, race_name):
        """Get race data by name"""
        return self._races.get(race_name)
    
    def get_all_races(self):
        """Get all available races"""
        return list(self._races.keys())
    
    def get_all_race_data(self):
        """Get all race data"""
        return self._races.copy()


# Global race loader instance
_race_loader = None


def get_race_loader():
    """Get the global race loader instance"""
    global _race_loader
    if _race_loader is None:
        _race_loader = RaceLoader()
    return _race_loader


def get_race_data(race_name):
    """
    Get race data for a specific race.
    
    Args:
        race_name (str): Name of the race
        
    Returns:
        dict: Race data or None if not found
    """
    loader = get_race_loader()
    return loader.get_race(race_name)


def get_all_races():
    """
    Get list of all available race names.
    
    Returns:
        list: List of race names
    """
    loader = get_race_loader()
    return loader.get_all_races()


def get_all_race_data():
    """
    Get all race data.
    
    Returns:
        dict: Dictionary of race names to race data
    """
    loader = get_race_loader()
    return loader.get_all_race_data()


def get_racial_ability_modifiers(race_name):
    """
    Get ability score modifiers for a race.
    
    Args:
        race_name (str): Name of the race
        
    Returns:
        dict: Ability modifiers organized by attribute category
    """
    race_data = get_race_data(race_name)
    if not race_data:
        return {}
    return race_data.get('ability_modifiers', {})


def apply_racial_bonuses(character, race_name):
    """
    Apply racial ability modifiers to a character's attributes.
    
    Args:
        character: Character model instance
        race_name (str): Name of the race
        
    Returns:
        bool: True if bonuses were applied, False otherwise
    """
    race_data = get_race_data(race_name)
    if not race_data:
        return False
    
    modifiers = race_data.get('ability_modifiers', {})
    
    # Initialize character attributes if needed
    if not character.attributes:
        character.attributes = {
            'body': {},
            'mind': {},
            'spirit': {},
            'kismet': {}
        }
    
    # Apply modifiers
    for prime_attr, sub_attrs in modifiers.items():
        if prime_attr not in character.attributes:
            character.attributes[prime_attr] = {}
        
        for sub_attr, modifier in sub_attrs.items():
            current_value = character.attributes[prime_attr].get(sub_attr, 0)
            character.attributes[prime_attr][sub_attr] = current_value + modifier
    
    return True


def get_racial_skills(race_name):
    """
    Get starting racial skills for a race.
    
    Args:
        race_name (str): Name of the race
        
    Returns:
        list: List of skill names
    """
    race_data = get_race_data(race_name)
    if not race_data:
        return []
    return race_data.get('racial_skills', [])


def get_racial_skill_bonuses(race_name):
    """
    Get skill bonuses for a race.
    
    Args:
        race_name (str): Name of the race
        
    Returns:
        dict: Dictionary of skill names to bonus values
    """
    race_data = get_race_data(race_name)
    if not race_data:
        return {}
    return race_data.get('skill_bonuses', {})


def get_wearable_slots(race_name):
    """
    Get available equipment slots for a race.
    
    Args:
        race_name (str): Name of the race
        
    Returns:
        list: List of wearable slot names
    """
    race_data = get_race_data(race_name)
    if not race_data:
        # Default slots if race not found
        return [
            "head", "neck", "chest", "shoulders", "arms", "hands", 
            "fingers", "waist", "legs", "feet", "wrist", "ears",
            "wield", "shield", "hold", "float", "sheath", "quiver"
        ]
    return race_data.get('wearable_slots', [])


def get_special_abilities(race_name):
    """
    Get special abilities for a race.
    
    Args:
        race_name (str): Name of the race
        
    Returns:
        list: List of special ability dicts
    """
    race_data = get_race_data(race_name)
    if not race_data:
        return []
    return race_data.get('special_abilities', [])


def get_resistances(race_name):
    """
    Get damage/effect resistances for a race.
    
    Args:
        race_name (str): Name of the race
        
    Returns:
        dict: Dictionary of resistance types to values
    """
    race_data = get_race_data(race_name)
    if not race_data:
        return {}
    return race_data.get('resistances', {})


def can_wear_slot(race_name, slot_name):
    """
    Check if a race can wear items in a specific slot.
    
    Args:
        race_name (str): Name of the race
        slot_name (str): Name of the equipment slot
        
    Returns:
        bool: True if the race can wear items in that slot
    """
    wearable_slots = get_wearable_slots(race_name)
    return slot_name in wearable_slots


def get_race_description(race_name):
    """
    Get the description for a race.
    
    Args:
        race_name (str): Name of the race
        
    Returns:
        str: Race description
    """
    race_data = get_race_data(race_name)
    if not race_data:
        return ""
    return race_data.get('description', '')


def get_base_speed(race_name):
    """
    Get base movement speed for a race.
    
    Args:
        race_name (str): Name of the race
        
    Returns:
        int: Base speed in feet
    """
    race_data = get_race_data(race_name)
    if not race_data:
        return 30  # Default speed
    return race_data.get('base_speed', 30)


def get_size(race_name):
    """
    Get size category for a race.
    
    Args:
        race_name (str): Name of the race
        
    Returns:
        str: Size category (tiny, small, medium, large)
    """
    race_data = get_race_data(race_name)
    if not race_data:
        return "medium"
    return race_data.get('size', 'medium')


def get_languages(race_name):
    """
    Get languages known by a race.
    
    Args:
        race_name (str): Name of the race
        
    Returns:
        tuple: (list of base languages, list of bonus language options)
    """
    race_data = get_race_data(race_name)
    if not race_data:
        return (["Common"], [])
    return (
        race_data.get('languages', ['Common']),
        race_data.get('bonus_languages', [])
    )

