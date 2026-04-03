from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from db import query
from datetime import date

attendance_bp = Blueprint("attendance", __name__)

def sync_student_bill(sid, att_date):
    """Automatically recalculate billing for the student when attendance changes."""
    ym = att_date[:7] # YYYY-MM
    # Calculate total meals for this month
    row = query(
        "SELECT COALESCE(SUM(breakfast+lunch+dinner),0) AS tm FROM attendance WHERE student_id=%s AND date LIKE %s",
        (sid, ym + "-%"), fetch="one"
    )
    tm = int(row["tm"])
    # Check if a bill already exists to preserve custom cost_per_meal and paid_amount
    b_row = query("SELECT cost_per_meal, paid_amount FROM billing WHERE student_id=%s AND month=%s", (sid, ym), fetch="one")
    cost = float(b_row["cost_per_meal"]) if b_row else 60.0
    paid = float(b_row["paid_amount"]) if b_row else 0.0
    total = round(tm * cost, 2)
    advance = max(0, round(paid - total, 2))
    
    if total == 0:
        status = "pending" if paid == 0 else "paid"
    else:
        status = "paid" if paid >= total else ("pending" if paid == 0 else "partial")

    query(
        """INSERT INTO billing (student_id, month, total_meals, cost_per_meal, total_amount, paid_amount, advance_amount, payment_status)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
           ON DUPLICATE KEY UPDATE total_meals=%s, total_amount=%s, advance_amount=%s, payment_status=%s""",
        (sid, ym, tm, cost, total, paid, advance, status, tm, total, advance, status),
        fetch="none"
    )

@attendance_bp.route("/", methods=["GET"])
@jwt_required()
def get_attendance():
    filter_date = request.args.get("date", date.today().isoformat())
    rows = query(
        """SELECT a.*, s.name, s.room_no
           FROM attendance a JOIN students s ON a.student_id=s.id
           WHERE a.date=%s ORDER BY s.name""",
        (filter_date,), fetch="all"
    )
    for r in rows:
        r["date"] = str(r["date"])
        r["created_at"] = str(r["created_at"])
    return jsonify(rows)

@attendance_bp.route("/student/<int:sid>", methods=["GET"])
@jwt_required()
def get_student_attendance(sid):
    month = request.args.get("month", date.today().strftime("%Y-%m"))
    rows = query(
        """SELECT * FROM attendance
           WHERE student_id=%s AND date LIKE %s
           ORDER BY date""",
        (sid, month + "-%"), fetch="all"
    )
    for r in rows:
        r["date"] = str(r["date"])
        r["created_at"] = str(r["created_at"])

    total_meals = sum(
        (1 if r["breakfast"] else 0) +
        (1 if r["lunch"] else 0) +
        (1 if r["dinner"] else 0)
        for r in rows
    )
    return jsonify({"records": rows, "total_meals": total_meals})

@attendance_bp.route("/mark", methods=["POST"])
@jwt_required()
def mark_attendance():
    d = request.get_json()
    sid       = d.get("student_id")
    att_date  = d.get("date", date.today().isoformat())
    breakfast = bool(d.get("breakfast", False))
    lunch     = bool(d.get("lunch", False))
    dinner    = bool(d.get("dinner", False))

    if not sid:
        return jsonify({"error": "student_id is required"}), 400

    # UPSERT attendance
    query(
        """INSERT INTO attendance (student_id, date, breakfast, lunch, dinner)
           VALUES (%s, %s, %s, %s, %s)
           ON DUPLICATE KEY UPDATE breakfast=%s, lunch=%s, dinner=%s""",
        (sid, att_date, breakfast, lunch, dinner, breakfast, lunch, dinner),
        fetch="none"
    )
    # Automatically sync billing!
    sync_student_bill(sid, att_date)

    return jsonify({"message": "Attendance marked successfully"})

@attendance_bp.route("/bulk-mark", methods=["POST"])
@jwt_required()
def bulk_mark():
    """Mark attendance for all active students at once."""
    d = request.get_json()
    att_date  = d.get("date", date.today().isoformat())
    breakfast = bool(d.get("breakfast", False))
    lunch     = bool(d.get("lunch", False))
    dinner    = bool(d.get("dinner", False))
    students  = d.get("students", [])   # list of student_ids

    for sid in students:
        query(
            """INSERT INTO attendance (student_id, date, breakfast, lunch, dinner)
               VALUES (%s, %s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE breakfast=%s, lunch=%s, dinner=%s""",
            (sid, att_date, breakfast, lunch, dinner, breakfast, lunch, dinner),
            fetch="none"
        )
        # Automatically sync billing for each student!
        sync_student_bill(sid, att_date)

    return jsonify({"message": f"Attendance marked for {len(students)} students"})

@attendance_bp.route("/summary", methods=["GET"])
@jwt_required()
def attendance_summary():
    """Monthly summary of meals per student."""
    month = request.args.get("month", date.today().strftime("%Y-%m"))
    rows = query(
        """SELECT s.id, s.name, s.room_no,
                  COUNT(a.id) AS days_present,
                  COALESCE(SUM(a.breakfast),0) AS total_breakfast,
                  COALESCE(SUM(a.lunch),0)     AS total_lunch,
                  COALESCE(SUM(a.dinner),0)    AS total_dinner,
                  COALESCE(SUM(a.breakfast+a.lunch+a.dinner),0) AS total_meals
           FROM students s
           LEFT JOIN attendance a ON s.id=a.student_id
               AND a.date LIKE %s
           WHERE s.status='active'
           GROUP BY s.id ORDER BY s.name""",
        (month + "-%",), fetch="all"
    )
    for r in rows:
        for k in ["days_present","total_breakfast","total_lunch","total_dinner","total_meals"]:
            r[k] = int(r[k])
    return jsonify(rows)
