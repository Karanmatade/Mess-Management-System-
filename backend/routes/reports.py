from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from db import query
from datetime import date

reports_bp = Blueprint("reports", __name__)

@reports_bp.route("/monthly-revenue", methods=["GET"])
@jwt_required()
def monthly_revenue():
    """Revenue per month for the past 12 months."""
    rows = query(
        """SELECT month,
                  COALESCE(SUM(total_amount),0) AS total_revenue,
                  COALESCE(SUM(paid_amount),0) AS paid_revenue,
                  COALESCE(SUM(advance_amount),0) AS advance_revenue,
                  COALESCE(SUM(CASE WHEN total_amount > paid_amount THEN total_amount - paid_amount ELSE 0 END),0) AS pending_revenue
           FROM billing
           WHERE month >= DATE_FORMAT(CURDATE() - INTERVAL 11 MONTH,'%%Y-%%m')
           GROUP BY month
           ORDER BY month""",
        fetch="all"
    )
    for r in rows:
        r["total_revenue"]   = float(r["total_revenue"])
        r["paid_revenue"]    = float(r["paid_revenue"])
        r["pending_revenue"] = float(r["pending_revenue"])
        r["advance_revenue"] = float(r["advance_revenue"])
    return jsonify(rows)

@reports_bp.route("/meal-consumption", methods=["GET"])
@jwt_required()
def meal_consumption():
    """Meal type breakdown per month for the last 6 months."""
    rows = query(
        """SELECT DATE_FORMAT(date,'%%Y-%%m') AS month,
                  SUM(breakfast) AS breakfast,
                  SUM(lunch)     AS lunch,
                  SUM(dinner)    AS dinner
           FROM attendance
           WHERE date >= CURDATE() - INTERVAL 6 MONTH
           GROUP BY DATE_FORMAT(date,'%%Y-%%m')
           ORDER BY month""",
        fetch="all"
    )
    for r in rows:
        r["breakfast"] = int(r["breakfast"] or 0)
        r["lunch"]     = int(r["lunch"] or 0)
        r["dinner"]    = int(r["dinner"] or 0)
    return jsonify(rows)

@reports_bp.route("/top-students", methods=["GET"])
@jwt_required()
def top_students():
    """Top 10 students by meal count this month."""
    month = request.args.get("month", date.today().strftime("%Y-%m"))
    rows = query(
        """SELECT s.name, s.room_no,
                  COALESCE(SUM(a.breakfast+a.lunch+a.dinner),0) AS total_meals
           FROM students s
           LEFT JOIN attendance a ON s.id=a.student_id
               AND DATE_FORMAT(a.date,'%%Y-%%m')=%s
           WHERE s.status='active'
           GROUP BY s.id ORDER BY total_meals DESC LIMIT 10""",
        (month,), fetch="all"
    )
    for r in rows:
        r["total_meals"] = int(r["total_meals"])
    return jsonify(rows)

@reports_bp.route("/payment-stats", methods=["GET"])
@jwt_required()
def payment_stats():
    month = request.args.get("month", date.today().strftime("%Y-%m"))
    row = query(
        """SELECT
              COUNT(*) AS total_bills,
              SUM(CASE WHEN payment_status='paid' THEN 1 ELSE 0 END) AS paid_count,
              SUM(CASE WHEN payment_status='pending' OR payment_status='partial' THEN 1 ELSE 0 END) AS pending_count,
              COALESCE(SUM(paid_amount),0) AS paid_amount,
              COALESCE(SUM(advance_amount),0) AS advance_amount,
              COALESCE(SUM(CASE WHEN total_amount > paid_amount THEN total_amount - paid_amount ELSE 0 END),0) AS pending_amount
           FROM billing WHERE month=%s""",
        (month,), fetch="one"
    )
    for k in ["total_bills","paid_count","pending_count"]:
        row[k] = int(row[k] or 0)
    for k in ["paid_amount","pending_amount","advance_amount"]:
        row[k] = float(row[k] or 0)
    return jsonify(row)
