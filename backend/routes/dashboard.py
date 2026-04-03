from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from db import query
from datetime import date

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/", methods=["GET"])
@jwt_required()
def get_dashboard():
    today = date.today().isoformat()
    current_month = date.today().strftime("%Y-%m")

    # Total active students
    total_students = query(
        "SELECT COUNT(*) AS cnt FROM students WHERE status='active'",
        fetch="one"
    )["cnt"]

    # Meals served today
    meal_row = query(
        """SELECT
              SUM(breakfast) + SUM(lunch) + SUM(dinner) AS meals_today
           FROM attendance WHERE date=%s""",
        (today,), fetch="one"
    )
    meals_today = meal_row["meals_today"] or 0

    # Monthly revenue (paid bills)
    rev_row = query(
        """SELECT COALESCE(SUM(total_amount),0) AS revenue
           FROM billing WHERE month=%s AND payment_status='paid'""",
        (current_month,), fetch="one"
    )
    monthly_revenue = float(rev_row["revenue"])

    # Pending payments count
    pending = query(
        "SELECT COUNT(*) AS cnt FROM billing WHERE payment_status='pending'",
        fetch="one"
    )["cnt"]

    # Pending amount
    pending_amt = query(
        "SELECT COALESCE(SUM(total_amount),0) AS amt FROM billing WHERE payment_status='pending'",
        fetch="one"
    )
    pending_amount = float(pending_amt["amt"])

    # Today's meal breakdown (breakfast / lunch / dinner)
    breakdown = query(
        """SELECT SUM(breakfast) AS b, SUM(lunch) AS l, SUM(dinner) AS d
           FROM attendance WHERE date=%s""",
        (today,), fetch="one"
    )

    # Recent students (last 5 added)
    recent_students = query(
        "SELECT id, name, room_no, status, created_at FROM students ORDER BY created_at DESC LIMIT 5",
        fetch="all"
    )

    # Attendance last 7 days (for chart)
    weekly_attendance = query(
        """SELECT date, SUM(breakfast+lunch+dinner) AS total
           FROM attendance
           WHERE date >= CURDATE() - INTERVAL 6 DAY
           GROUP BY date
           ORDER BY date""",
        fetch="all"
    )
    for row in weekly_attendance:
        row["date"] = str(row["date"])
        row["total"] = int(row["total"] or 0)

    for s in recent_students:
        s["created_at"] = str(s["created_at"])

    return jsonify({
        "total_students":   total_students,
        "meals_today":      int(meals_today),
        "monthly_revenue":  monthly_revenue,
        "pending_payments": pending,
        "pending_amount":   pending_amount,
        "meal_breakdown":   {
            "breakfast": int(breakdown["b"] or 0),
            "lunch":     int(breakdown["l"] or 0),
            "dinner":    int(breakdown["d"] or 0),
        },
        "recent_students":    recent_students,
        "weekly_attendance":  weekly_attendance,
    })
