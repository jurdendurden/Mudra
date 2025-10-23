from app import create_app, socketio
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import os

# Create Flask application
app = create_app()

if __name__ == '__main__':
    from map_builder import app as map_builder_app
    # Mount the map builder app at /map-builder
    application = DispatcherMiddleware(app, {
        '/map-builder': map_builder_app
    })
    import eventlet
    import eventlet.wsgi
    # Run the combined app using eventlet's WSGI server
    eventlet.wsgi.server(
        eventlet.listen(('0.0.0.0', int(os.environ.get('PORT', 5000)))),
        application
    )

    
