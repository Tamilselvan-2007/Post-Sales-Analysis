from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    from flask import Flask
    app = Flask(__name__)

    # Register blueprints
    from .routes.detect_routes import detect_bp
    app.register_blueprint(detect_bp)

    # Initialize SIO
    socketio.init_app(app)

    return app
