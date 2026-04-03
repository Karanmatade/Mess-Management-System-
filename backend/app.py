from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET", "mess@SecretKey#2024!")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 60 * 60 * 8   # 8 hours

bcrypt = Bcrypt(app)
jwt    = JWTManager(app)

# ── Register blueprints ─────────────────────────────────────────────────────
from routes.auth       import auth_bp
from routes.dashboard  import dashboard_bp
from routes.students   import students_bp
from routes.attendance import attendance_bp
from routes.menu       import menu_bp
from routes.billing    import billing_bp
from routes.reports    import reports_bp

app.register_blueprint(auth_bp,       url_prefix="/api/auth")
app.register_blueprint(dashboard_bp,  url_prefix="/api/dashboard")
app.register_blueprint(students_bp,   url_prefix="/api/students")
app.register_blueprint(attendance_bp, url_prefix="/api/attendance")
app.register_blueprint(menu_bp,       url_prefix="/api/menu")
app.register_blueprint(billing_bp,    url_prefix="/api/billing")
app.register_blueprint(reports_bp,    url_prefix="/api/reports")

@app.route("/")
def index():
    return jsonify({"message": "Mess Management API v1.0", "status": "running"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
