from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import query
from datetime import date

meals_bp = Blueprint("meals", __name__)

def _get_identity():
    import json
    raw = get_jwt_identity()
    try:
        return json.loads(raw)
    except:
        return raw

@meals_bp.route("/mark", methods=["POST"])
@jwt_required()
def mark_meal():
    identity = _get_identity()
    if isinstance(identity, dict):
        uid = identity.get("id")
    else:
        return jsonify({"error": "Admin cannot mark meal here"}), 403
        
    data = request.get_json()
    meal_type = data.get("meal_type")
    dt = data.get("date", str(date.today()))
    action = data.get("action", "mark") # 'mark' or 'unmark'
    
    if meal_type not in ["Breakfast", "Lunch", "Dinner"]:
        return jsonify({"error": "Invalid meal type"}), 400
        
    if action == "mark":
        query("INSERT IGNORE INTO meals (user_id, date, meal_type) VALUES (%s, %s, %s)", (uid, dt, meal_type), fetch="none")
        return jsonify({"message": f"{meal_type} marked for {dt}"})
    else:
        query("DELETE FROM meals WHERE user_id=%s AND date=%s AND meal_type=%s", (uid, dt, meal_type), fetch="none")
        return jsonify({"message": f"{meal_type} unmarked for {dt}"})

@meals_bp.route("/my-meals", methods=["GET"])
@jwt_required()
def get_my_meals():
    identity = _get_identity()
    if isinstance(identity, dict):
        uid = identity.get("id")
    else:
        return jsonify({"error": "Unauthorized"}), 403
        
    rows = query("SELECT date, meal_type FROM meals WHERE user_id=%s ORDER BY date DESC LIMIT 50", (uid,), fetch="all")
    for r in rows:
        r["date"] = str(r["date"])
        
    return jsonify(rows)

@meals_bp.route("/today", methods=["GET"])
@jwt_required()
def get_today_meals():
    identity = _get_identity()
    if isinstance(identity, dict):
        uid = identity.get("id")
    else:
        return jsonify({}), 400
    
    today = str(date.today())
    rows = query("SELECT meal_type FROM meals WHERE user_id=%s AND date=%s", (uid, today), fetch="all")
    marked = [r["meal_type"] for r in rows]
    return jsonify({"marked": marked})
