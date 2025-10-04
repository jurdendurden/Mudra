import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///mud_game.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # SocketIO configuration
    SOCKETIO_ASYNC_MODE = 'eventlet'
    
    # Game configuration
    GAME_TICK_RATE = 100  # milliseconds
    MAX_PLAYERS = 100
    STARTING_TRIAL_POINTS = 20
    STARTING_PROGRESS_POINTS = 0
    STARTING_LOCATION = 'room_001'
    
    # Attribute caps
    ATTRIBUTE_CAPS = {
        'body': 400,
        'mind': 400,
        'spirit': 400,
        'kismet': 200
    }
    
    # Progression settings
    PROGRESSION_CONFIG = {
        'trial_point_sources': {
            'combat_kill': 1,
            'quest_completion': 5,
            'exploration': 0.5
        },
        'progress_point_sources': {
            'skill_use': 0.1,
            'spell_cast': 0.2,
            'craft_success': 1
        },
        'attribute_costs': {
            'formula': 'current_value * 0.5'
        }
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}