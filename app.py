from app import create_app, socketio
import os

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Run the application
    socketio.run(
        app,
        debug=app.config['DEBUG'],
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )
