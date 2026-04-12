from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

load_dotenv()

# Frontend static files directory
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config["JWT_SECRET_KEY"]          = os.getenv("JWT_SECRET", "mess@SecretKey#2024!")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 60 * 60 * 8   # 8 hours
app.config["JWT_TOKEN_LOCATION"]       = ["headers", "query_string"]

bcrypt = Bcrypt(app)
jwt    = JWTManager(app)

from routes.auth       import auth_bp
from routes.dashboard  import dashboard_bp
from routes.students   import students_bp
from routes.attendance import attendance_bp
from routes.menu       import menu_bp
from routes.billing    import billing_bp
from routes.reports    import reports_bp
from routes.meals      import meals_bp

app.register_blueprint(auth_bp,       url_prefix="/api/auth")
app.register_blueprint(dashboard_bp,  url_prefix="/api/dashboard")
app.register_blueprint(students_bp,   url_prefix="/api/students")
app.register_blueprint(attendance_bp, url_prefix="/api/attendance")
app.register_blueprint(menu_bp,       url_prefix="/api/menu")
app.register_blueprint(billing_bp,    url_prefix="/api/billing")
app.register_blueprint(reports_bp,    url_prefix="/api/reports")
app.register_blueprint(meals_bp,      url_prefix="/api/meals")

# ── Serve frontend ─────────────────────────────────────────
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    # Don't intercept /api/* routes
    if filename.startswith("api/"):
        return jsonify({"error": "Not found"}), 404
    try:
        return send_from_directory(app.static_folder, filename)
    except Exception:
        return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
