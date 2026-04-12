from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from db import query
from datetime import date

reports_bp = Blueprint("reports", __name__)

@reports_bp.route("/monthly-revenue", methods=["GET"])
@jwt_required()
def monthly_revenue():
    """Revenue per month for the past 12 months based on billing end date."""
    rows = query(
        """SELECT DATE_FORMAT(cycle_end, '%%Y-%%m') as month,
                  COALESCE(SUM(total_bill), 0) AS total_revenue,
                  COALESCE(SUM(CASE WHEN status='paid' THEN total_bill ELSE 0 END), 0) AS paid_revenue,
                  0 AS advance_revenue,
                  COALESCE(SUM(CASE WHEN status='pending' THEN total_bill ELSE 0 END), 0) AS pending_revenue
           FROM billing
           WHERE cycle_end >= DATE_FORMAT(CURDATE() - INTERVAL 11 MONTH, '%%Y-%%m-01')
           GROUP BY DATE_FORMAT(cycle_end, '%%Y-%%m')
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
        """SELECT DATE_FORMAT(date, '%%Y-%%m') AS month,
                  SUM(CASE WHEN meal_type='Breakfast' THEN 1 ELSE 0 END) AS breakfast,
                  SUM(CASE WHEN meal_type='Lunch' THEN 1 ELSE 0 END) AS lunch,
                  SUM(CASE WHEN meal_type='Dinner' THEN 1 ELSE 0 END) AS dinner
           FROM meals
           WHERE date >= CURDATE() - INTERVAL 6 MONTH
           GROUP BY DATE_FORMAT(date, '%%Y-%%m')
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
        """SELECT s.name, s.room_no, COUNT(m.id) AS total_meals
           FROM students s
           LEFT JOIN meals m ON s.id=m.user_id AND DATE_FORMAT(m.date, '%%Y-%%m')=%s
           WHERE s.status='active'
           GROUP BY s.id ORDER BY total_meals DESC LIMIT 10""",
        (month,), fetch="all"
    )
    for r in rows:
        r["total_meals"] = int(r["total_meals"] or 0)
    return jsonify(rows)

@reports_bp.route("/payment-stats", methods=["GET"])
@jwt_required()
def payment_stats():
    """Stats based on billing cycles ending in the given month."""
    month = request.args.get("month", date.today().strftime("%Y-%m"))
    row = query(
        """SELECT
              COUNT(*) AS total_bills,
              SUM(CASE WHEN status='paid' THEN 1 ELSE 0 END) AS paid_count,
              SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) AS pending_count,
              COALESCE(SUM(CASE WHEN status='paid' THEN total_bill ELSE 0 END),0) AS paid_amount,
              0 AS advance_amount,
              COALESCE(SUM(CASE WHEN status='pending' THEN total_bill ELSE 0 END),0) AS pending_amount
           FROM billing WHERE DATE_FORMAT(cycle_end, '%%Y-%%m')=%s""",
        (month,), fetch="one"
    )
    for k in ["total_bills","paid_count","pending_count"]:
        row[k] = int(row[k] or 0)
    for k in ["paid_amount","pending_amount","advance_amount"]:
        row[k] = float(row[k] or 0)
    return jsonify(row)
