from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from db import query
from datetime import date

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/", methods=["GET"])
@jwt_required()
def get_dashboard():
    today = date.today().isoformat()
    current_month_start = date.today().replace(day=1).isoformat()

    # Total active students
    total_students = query(
        "SELECT COUNT(*) AS cnt FROM students WHERE status='active'",
        fetch="one"
    )["cnt"]

    # Meals served today
    meal_row = query(
        "SELECT COUNT(*) AS meals_today FROM meals WHERE date=%s",
        (today,), fetch="one"
    )
    meals_today = meal_row["meals_today"] or 0

    # Monthly revenue (paid bills)
    rev_row = query(
        "SELECT COALESCE(SUM(total_bill),0) AS revenue FROM billing WHERE status='paid' AND cycle_end >= %s",
        (current_month_start,), fetch="one"
    )
    monthly_revenue = float(rev_row["revenue"])

    # Pending payments count
    pending = query(
        "SELECT COUNT(*) AS cnt FROM billing WHERE status='pending'",
        fetch="one"
    )["cnt"]

    # Pending amount
    pending_amt = query(
        "SELECT COALESCE(SUM(total_bill),0) AS amt FROM billing WHERE status='pending'",
        fetch="one"
    )
    pending_amount = float(pending_amt["amt"])

    # Today's meal breakdown
    b = query("SELECT COUNT(*) as cnt FROM meals WHERE date=%s AND meal_type='Breakfast'", (today,), fetch="one")["cnt"]
    l = query("SELECT COUNT(*) as cnt FROM meals WHERE date=%s AND meal_type='Lunch'", (today,), fetch="one")["cnt"]
    d = query("SELECT COUNT(*) as cnt FROM meals WHERE date=%s AND meal_type='Dinner'", (today,), fetch="one")["cnt"]

    # Active Cycles (replacing recent students, using the logic we wrote in billing)
    students = query("SELECT id, name, room_no, status, date_of_joining, cycle_start_date FROM students WHERE status='active' ORDER BY id ASC", fetch="all")
    recent_students = []
    
    td = date.today()
    for s in students:
        s["created_at"] = str(s["date_of_joining"]) # reuse
        c_start = s["cycle_start_date"]
        days_rem = 30
        if c_start:
            days_rem = max(0, 30 - (td - c_start).days)
        recent_students.append({
            "name": s["name"],
            "room_no": s["room_no"],
            "status": "warning" if days_rem <= 5 else s["status"],
            "days_rem": days_rem
        })

    # Attendance last 7 days
    weekly_attendance = query(
        """SELECT date, COUNT(*) AS total
           FROM meals
           WHERE date >= CURDATE() - INTERVAL 6 DAY
           GROUP BY date
           ORDER BY date""",
        fetch="all"
    )
    for row in weekly_attendance:
        row["date"] = str(row["date"])
        row["total"] = int(row["total"] or 0)

    return jsonify({
        "total_students":   total_students,
        "meals_today":      int(meals_today),
        "monthly_revenue":  monthly_revenue,
        "pending_payments": pending,
        "pending_amount":   pending_amount,
        "meal_breakdown":   {
            "breakfast": b,
            "lunch":     l,
            "dinner":    d,
        },
        "recent_students":    recent_students,
        "weekly_attendance":  weekly_attendance,
    })
