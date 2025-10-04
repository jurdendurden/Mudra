from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_migrate import Migrate
import redis
import os

# Initialize extensions
db = SQLAlchemy()
socketio = SocketIO()
login_manager = LoginManager()
migrate = Migrate()
redis_client = None

def create_app(config_name=None):
    """Application factory pattern"""
    import os
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize Redis
    global redis_client
    redis_client = redis.from_url(app.config['REDIS_URL'])
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        from app.models.player import Player
        return Player.query.get(int(user_id))
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.game import game_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(game_bp, url_prefix='/game')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Root route
    @app.route('/')
    def index():
        from flask_login import current_user
        if current_user.is_authenticated:
            return redirect(url_for('game.index'))
        else:
            return redirect(url_for('auth.login'))
    
    # Register socket handlers
    from app.socket_handlers.game_events import register_game_events
    from app.socket_handlers.chat_events import register_chat_events
    
    register_game_events(socketio)
    register_chat_events(socketio)
    
    # Import models for migration
    from app.models import player, character, item, room
    
    return app

def get_redis():
    """Get Redis client instance"""
    return redis_client
