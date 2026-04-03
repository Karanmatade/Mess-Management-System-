from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from db import query

auth_bp = Blueprint("auth", __name__)
bcrypt  = Bcrypt()

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    admin = query("SELECT * FROM admin WHERE username=%s", (username,), fetch="one")
    if not admin:
        return jsonify({"error": "Invalid credentials"}), 401

    if not bcrypt.check_password_hash(admin["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=str(admin["id"]))
    return jsonify({
        "token": token,
        "username": admin["username"],
        "message": "Login successful"
    })

@auth_bp.route("/change-password", methods=["POST"])
def change_password():
    data = request.get_json()
    username    = data.get("username", "").strip()
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")

    admin = query("SELECT * FROM admin WHERE username=%s", (username,), fetch="one")
    if not admin or not bcrypt.check_password_hash(admin["password"], old_password):
        return jsonify({"error": "Invalid credentials"}), 401

    hashed = bcrypt.generate_password_hash(new_password).decode("utf-8")
    query("UPDATE admin SET password=%s WHERE username=%s", (hashed, username), fetch="none")
    return jsonify({"message": "Password changed successfully"})
