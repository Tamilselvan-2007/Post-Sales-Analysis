import logging
import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO

from routes.upload_routes import upload_bp
from routes.detect_routes import detect_bp
from routes.debug_routes import debug_bp
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

    # Attach socketio to app
    socketio.init_app(app)

    # Make socketio accessible from blueprints
    app.socketio = socketio

    # Register Blueprints
    app.register_blueprint(upload_bp)
    app.register_blueprint(detect_bp)
    app.register_blueprint(debug_bp)

    register_frontend_routes(app)
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

    @app.route("/user_login")
    def user_login():
        return render_template("login_page.html")

    @app.route("/admin_login")
    def admin_login():
        return render_template("login_admin.html")

    @app.route("/admin_training_area")
    def admin_training_area():
        return render_template("admin_use_page.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("second_page.html")

    @app.route("/login", methods=["POST"])
    def login():
        user_type = request.form.get("user_type", "user")
        if user_type == "admin":
            user_id = request.form.get("Admin_id", "").strip()
        else:
            user_id = request.form.get("technician_id", "").strip()
        password = request.form.get("password", "")

        if user_type == "user" and user_id == "technician_1" and password == "tech@1":
            session["user_id"] = user_id
            return redirect(url_for("dashboard"))

        if user_type == "admin" and user_id == "admin_1" and password == "admin@1":
            session["user_id"] = user_id
            return redirect(url_for("admin_training_area"))

        if user_type == "admin":
            return redirect(url_for("admin_login") + "?error=invalid")
        return redirect(url_for("user_login") + "?error=invalid")

    @app.route("/missing")
    def missing_page():
        return render_template("third_page.html", page_type="missing")

    @app.route("/burnt")
    def burnt_page():
        return render_template("third_page.html", page_type="burnt")

    @app.route("/voltage")
    def voltage_page():
        return render_template("fifth_page.html")

    @app.route("/diagnosis_complete")
    def diagnosis_complete():
        return render_template("diagnosis_page.html")
        


app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)   # <--- IMPORTANT
