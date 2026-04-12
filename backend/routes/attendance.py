from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from db import query
from datetime import date

attendance_bp = Blueprint("attendance", __name__)

@attendance_bp.route("/", methods=["GET"])
@jwt_required()
def get_attendance():
    filter_date = request.args.get("date", date.today().isoformat())
    rows = query("SELECT user_id, meal_type FROM meals WHERE date=%s", (filter_date,), fetch="all")
    
    att_dict = {}
    for r in rows:
        uid = r["user_id"]
        if uid not in att_dict:
            att_dict[uid] = {"student_id": uid, "date": filter_date, "breakfast": False, "lunch": False, "dinner": False}
        
        mtype = r["meal_type"]
        if mtype == "Breakfast": att_dict[uid]["breakfast"] = True
        elif mtype == "Lunch": att_dict[uid]["lunch"] = True
        elif mtype == "Dinner": att_dict[uid]["dinner"] = True
        
    return jsonify(list(att_dict.values()))

@attendance_bp.route("/day-detail", methods=["GET"])
@jwt_required()
def get_day_detail():
    """Return ALL active students with their B/L/D status for a given date.
    Used by calendar click to show the full editable attendance panel."""
    filter_date = request.args.get("date", date.today().isoformat())
    
    # Get all active students
    students = query(
        "SELECT id, name, room_no, email FROM students WHERE status='active' ORDER BY id ASC",
        fetch="all"
    )
    
    # Get existing meal records for this date
    meals = query(
        "SELECT user_id, meal_type FROM meals WHERE date=%s",
        (filter_date,), fetch="all"
    )
    
    meal_map = {}
    for m in meals:
        uid = m["user_id"]
        if uid not in meal_map:
            meal_map[uid] = {"breakfast": False, "lunch": False, "dinner": False}
        mt = m["meal_type"]
        if mt == "Breakfast": meal_map[uid]["breakfast"] = True
        elif mt == "Lunch":   meal_map[uid]["lunch"]    = True
        elif mt == "Dinner":  meal_map[uid]["dinner"]   = True
    
    result = []
    for s in students:
        att = meal_map.get(s["id"], {"breakfast": False, "lunch": False, "dinner": False})
        result.append({
            "student_id": s["id"],
            "name": s["name"],
            "room_no": s["room_no"],
            "email": s.get("email", ""),
            "breakfast": att["breakfast"],
            "lunch":     att["lunch"],
            "dinner":    att["dinner"],
        })
    
    return jsonify({"date": filter_date, "students": result})

@attendance_bp.route("/month-dots", methods=["GET"])
@jwt_required()
def get_month_dots():
    """Return per-day meal counts for an entire month in a single query —
    used to render calendar dots fast without 30 individual API calls."""
    month = request.args.get("month", date.today().strftime("%Y-%m"))
    sid   = request.args.get("student_id", "")
    
    if sid:
        rows = query(
            """SELECT date, 
                      SUM(CASE WHEN meal_type='Breakfast' THEN 1 ELSE 0 END) AS b,
                      SUM(CASE WHEN meal_type='Lunch'     THEN 1 ELSE 0 END) AS l,
                      SUM(CASE WHEN meal_type='Dinner'    THEN 1 ELSE 0 END) AS d
               FROM meals WHERE user_id=%s AND date LIKE %s
               GROUP BY date""",
            (sid, month + "-%"), fetch="all"
        )
    else:
        rows = query(
            """SELECT date,
                      SUM(CASE WHEN meal_type='Breakfast' THEN 1 ELSE 0 END) AS b,
                      SUM(CASE WHEN meal_type='Lunch'     THEN 1 ELSE 0 END) AS l,
                      SUM(CASE WHEN meal_type='Dinner'    THEN 1 ELSE 0 END) AS d
               FROM meals WHERE date LIKE %s
               GROUP BY date""",
            (month + "-%",), fetch="all"
        )
    
    result = {}
    for r in rows:
        result[str(r["date"])] = {"b": int(r["b"] or 0), "l": int(r["l"] or 0), "d": int(r["d"] or 0)}
    
    return jsonify(result)

@attendance_bp.route("/student/<int:sid>", methods=["GET"])
@jwt_required()
def get_student_attendance(sid):
    month = request.args.get("month", date.today().strftime("%Y-%m"))
    rows = query("SELECT date, meal_type FROM meals WHERE user_id=%s AND date LIKE %s ORDER BY date", (sid, month+"-%"), fetch="all")
    
    att_dict = {}
    total_meals = 0
    for r in rows:
        d_str = str(r["date"])
        if d_str not in att_dict:
            att_dict[d_str] = {"student_id": sid, "date": d_str, "breakfast": False, "lunch": False, "dinner": False}
            
        mtype = r["meal_type"]
        if mtype == "Breakfast": att_dict[d_str]["breakfast"] = True
        elif mtype == "Lunch": att_dict[d_str]["lunch"] = True
        elif mtype == "Dinner": att_dict[d_str]["dinner"] = True
        total_meals += 1
        
    return jsonify({"records": list(att_dict.values()), "total_meals": total_meals})

@attendance_bp.route("/mark", methods=["POST"])
@jwt_required()
def mark_attendance():
    d = request.get_json()
    sid       = d.get("student_id")
    att_date  = d.get("date", date.today().isoformat())
    b = bool(d.get("breakfast", False))
    l = bool(d.get("lunch", False))
    din = bool(d.get("dinner", False))
    
    if not sid:
        return jsonify({"error": "student_id is required"}), 400

    query("DELETE FROM meals WHERE user_id=%s AND date=%s", (sid, att_date), fetch="none")
    
    inserts = []
    if b: inserts.append((sid, att_date, "Breakfast"))
    if l: inserts.append((sid, att_date, "Lunch"))
    if din: inserts.append((sid, att_date, "Dinner"))
    
    for ins in inserts:
        query("INSERT IGNORE INTO meals (user_id, date, meal_type) VALUES (%s, %s, %s)", ins, fetch="none")
        
    return jsonify({"message": "Attendance marked successfully"})

@attendance_bp.route("/summary", methods=["GET"])
@jwt_required()
def attendance_summary():
    """Monthly summary of meals per student."""
    month = request.args.get("month", date.today().strftime("%Y-%m"))
    rows = query(
        """SELECT s.id, s.name, s.room_no,
                  COUNT(DISTINCT m.date) AS days_present,
                  SUM(CASE WHEN m.meal_type='Breakfast' THEN 1 ELSE 0 END) AS total_breakfast,
                  SUM(CASE WHEN m.meal_type='Lunch' THEN 1 ELSE 0 END) AS total_lunch,
                  SUM(CASE WHEN m.meal_type='Dinner' THEN 1 ELSE 0 END) AS total_dinner,
                  COUNT(m.id) AS total_meals
           FROM students s
           LEFT JOIN meals m ON s.id=m.user_id AND m.date LIKE %s
           WHERE s.status='active'
           GROUP BY s.id ORDER BY s.id ASC""",
        (month + "-%",), fetch="all"
    )
    for r in rows:
        for k in ["days_present","total_breakfast","total_lunch","total_dinner","total_meals"]:
            r[k] = int(r[k] or 0)
    return jsonify(rows)
