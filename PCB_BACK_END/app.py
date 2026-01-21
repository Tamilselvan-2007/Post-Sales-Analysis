import logging
import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO
from flask_cors import CORS

from routes.upload_routes import upload_bp
from routes.detect_routes import detect_bp
from routes.debug_routes import debug_bp
from model.load_models import load_models
import traceback

LOG_FORMAT = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"


socketio = SocketIO(cors_allowed_origins="*")   # <--- ADD THIS


def create_app() -> Flask:
    app = Flask(
        __name__,
        static_folder="static",
        static_url_path="/static",
        template_folder="templates"
    )

    configure_app(app)
    setup_logging(app)
    register_error_handlers(app)
    
    # Enable CORS for all routes
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Attach socketio to app
    socketio.init_app(app)

    # Make socketio accessible from blueprints
    app.socketio = socketio

    # Register Blueprints
    app.register_blueprint(upload_bp)
    app.register_blueprint(detect_bp)
    app.register_blueprint(debug_bp)

    register_frontend_routes(app)
    
    # Load ML models at startup for better performance
    app.logger.info("🔄 Loading ML models at startup...")
    try:
        load_models()
        app.logger.info("✅ ML models loaded successfully!")
    except Exception as e:
        app.logger.error(f"❌ Failed to load ML models: {e}")
        app.logger.warning("⚠️  Application will continue but detection endpoints may fail")
    
    return app


def configure_app(app: Flask) -> None:
    app.config["SECRET_KEY"] = "your-secret-key-here"
    app.config["UPLOAD_FOLDER"] = None
    app.config.setdefault("MAX_CONTENT_LENGTH", 32 * 1024 * 1024)
    app.config.setdefault("JSON_SORT_KEYS", False)


def setup_logging(app: Flask) -> None:
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    app.logger.setLevel(logging.INFO)


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return {"success": False, "error": {"message": "File too large. Maximum size is 32MB."}}, 413

    @app.errorhandler(404)
    def page_not_found(error):
        if request.path.startswith("/detect/"):
            return {"success": False, "error": {"message": "Endpoint not found."}}, 404
        return render_template("first_page.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return {"success": False, "error": {"message": "Internal Server Error", "trace": traceback.format_exc()}}, 500



def register_frontend_routes(app: Flask):

    @app.route("/")
    def home():
        return render_template("first_page.html")

    @app.route("/admin_training_area")
    def admin_training_area():
        return render_template("admin_use_page.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("second_page.html")

    @app.route("/missing", methods=['GET', 'POST'])
    def missing_page():
        return render_template("third_page.html", page_type="missing")

    @app.route("/burnt", methods=['GET', 'POST'])
    def burnt_page():
        return render_template("third_page.html", page_type="burnt")

    @app.route("/voltage", methods=['GET', 'POST'])
    def voltage_page():
        return render_template("fifth_page.html")

    @app.route("/diagnosis_complete", methods=['GET', 'POST'])
    def diagnosis_complete():
        return render_template("diagnosis_page.html")
        


app = create_app()

if __name__ == "__main__":
    socketio.run(app)
