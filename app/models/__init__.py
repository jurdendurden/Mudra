# Import all models for SQLAlchemy to discover them
from .player import Player
from .character import Character
from .npc import NPC
from .item import Item, ItemTemplate
from .room import Room, Area
from .skill import Skill, CharacterSkill
from .spell import Spell, CharacterSpell
from .chat_message import ChatMessage

__all__ = [
    'Player', 'Character', 'NPC', 'Item', 'ItemTemplate', 
    'Room', 'Area', 'Skill', 'CharacterSkill', 
    'Spell', 'CharacterSpell', 'ChatMessage'
]
