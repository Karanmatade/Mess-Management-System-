from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from db import query

menu_bp = Blueprint("menu", __name__)

DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

@menu_bp.route("/", methods=["GET"])
@jwt_required()
def get_menu():
    rows = query("SELECT * FROM menu ORDER BY FIELD(day,'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')",
                 fetch="all")
    for r in rows:
        r["updated_at"] = str(r["updated_at"])
    return jsonify(rows)

@menu_bp.route("/<string:day>", methods=["GET"])
@jwt_required()
def get_day_menu(day):
    row = query("SELECT * FROM menu WHERE day=%s", (day.capitalize(),), fetch="one")
    if not row:
        return jsonify({"error": "Day not found"}), 404
    row["updated_at"] = str(row["updated_at"])
    return jsonify(row)

@menu_bp.route("/today", methods=["GET"])
@jwt_required()
def get_today_menu():
    from datetime import date
    day_name = date.today().strftime("%A")
    row = query("SELECT * FROM menu WHERE day=%s", (day_name,), fetch="one")
    if not row:
        return jsonify({"error": "Menu not found"}), 404
    row["updated_at"] = str(row["updated_at"])
    return jsonify(row)

@menu_bp.route("/<string:day>", methods=["PUT"])
@jwt_required()
def update_menu(day):
    d = request.get_json()
    day = day.capitalize()
    if day not in DAYS:
        return jsonify({"error": "Invalid day"}), 400

    query(
        """INSERT INTO menu (day, breakfast, lunch, dinner)
           VALUES (%s, %s, %s, %s)
           ON DUPLICATE KEY UPDATE breakfast=%s, lunch=%s, dinner=%s""",
        (day, d.get("breakfast",""), d.get("lunch",""), d.get("dinner",""),
             d.get("breakfast",""), d.get("lunch",""), d.get("dinner","")),
        fetch="none"
    )
    return jsonify({"message": f"Menu for {day} updated successfully"})

@menu_bp.route("/bulk", methods=["PUT"])
@jwt_required()
def bulk_update_menu():
    """Update entire week's menu at once. Body: [{day, breakfast, lunch, dinner}, ...]"""
    items = request.get_json()
    for item in items:
        day = item.get("day","").capitalize()
        if day not in DAYS:
            continue
        query(
            """INSERT INTO menu (day, breakfast, lunch, dinner)
               VALUES (%s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE breakfast=%s, lunch=%s, dinner=%s""",
            (day, item.get("breakfast",""), item.get("lunch",""), item.get("dinner",""),
                  item.get("breakfast",""), item.get("lunch",""), item.get("dinner","")),
            fetch="none"
        )
    return jsonify({"message": "Weekly menu updated successfully"})
