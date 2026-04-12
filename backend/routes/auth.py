from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from db import query
from datetime import date

auth_bp = Blueprint("auth", __name__)
bcrypt  = Bcrypt()

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    date_of_joining = data.get("date_of_joining") or str(date.today())

    if not name or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    existing = query("SELECT id FROM students WHERE email=%s", (email,), fetch="one")
    if existing:
        return jsonify({"error": "Email already exists"}), 400

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    
    new_id = query(
        "INSERT INTO students (name, email, password, date_of_joining, cycle_start_date, room_no) VALUES(%s, %s, %s, %s, %s, 'N/A')",
        (name, email, hashed, date_of_joining, date_of_joining),
        fetch="none"
    )
    
    return jsonify({"message": "User registered successfully", "id": new_id}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    import json
    data = request.get_json()
    username = data.get("username", "").strip() # can be admin user or student email
    password = data.get("password", "")

    # Check admin
    admin = query("SELECT * FROM admin WHERE username=%s", (username,), fetch="one")
    if admin and bcrypt.check_password_hash(admin["password"], password):
        token = create_access_token(identity=json.dumps({"id": admin["id"], "role": "admin"}))
        return jsonify({
            "token": token,
            "username": admin["username"],
            "role": "admin",
            "message": "Login successful"
        })

    # Check student
    student = query("SELECT * FROM students WHERE email=%s", (username,), fetch="one")
    if student and student.get("password") and bcrypt.check_password_hash(student["password"], password):
        token = create_access_token(identity=json.dumps({"id": student["id"], "role": "student"}))
        return jsonify({
            "token": token,
            "username": student["name"],
            "role": "student",
            "message": "Login successful"
        })

    return jsonify({"error": "Invalid credentials"}), 401

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
