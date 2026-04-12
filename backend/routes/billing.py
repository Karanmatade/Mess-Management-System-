import csv
import io
import json
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import query
from datetime import date, timedelta
import math

billing_bp = Blueprint("billing", __name__)

def get_meal_costs():
    """Get meal costs from settings."""
    costs = {"Breakfast": 30.0, "Lunch": 40.0, "Dinner": 40.0}
    try:
        rows = query("SELECT k, val FROM settings WHERE k IN ('cost_breakfast', 'cost_lunch', 'cost_dinner', 'cost_per_meal')", fetch="all")
        keys_found = [r["k"] for r in rows]
        for r in rows:
            if r["k"] == "cost_breakfast": costs["Breakfast"] = float(r["val"])
            elif r["k"] == "cost_lunch": costs["Lunch"] = float(r["val"])
            elif r["k"] == "cost_dinner": costs["Dinner"] = float(r["val"])
            elif r["k"] == "cost_per_meal" and "cost_breakfast" not in keys_found:
                costs["Breakfast"] = costs["Lunch"] = costs["Dinner"] = float(r["val"])
    except Exception:
        pass
    return costs

def calc_bill_for_period(uid, start_date, end_date):
    costs = get_meal_costs()
    rows = query("SELECT meal_type, COUNT(*) as cnt FROM meals WHERE user_id=%s AND date >= %s AND date <= %s GROUP BY meal_type", (uid, start_date, end_date), fetch="all")
    total_meals = 0
    total_bill = 0.0
    for r in rows:
        cnt = r["cnt"]
        mtype = r["meal_type"]
        total_meals += cnt
        total_bill += cnt * costs.get(mtype, 40.0)
    return total_meals, total_bill

def parse_identity(identity_raw):
    """Parse JWT identity whether it's a string, JSON string, or dict."""
    if isinstance(identity_raw, dict):
        return identity_raw
    try:
        return json.loads(identity_raw)
    except Exception:
        if identity_raw == "admin":
            return {"id": 1, "role": "admin"}
        return {"id": int(identity_raw) if str(identity_raw).isdigit() else 0, "role": "student"}

def run_billing_automation(user_id=None):
    """Generate bills for completed 30-day cycles, AND ensure every active student
    has a current-cycle bill so they appear in the billing table."""
    today = date.today()
    sql = "SELECT id, date_of_joining, cycle_start_date FROM students WHERE status='active'"
    params = []
    if user_id:
        sql += " AND id=%s"
        params.append(user_id)
        
    students = query(sql, params, fetch="all")
    generated = 0
    
    for s in students:
        cycle_start = s.get("cycle_start_date")
        if not cycle_start:
            cycle_start = s.get("date_of_joining") or today
            query("UPDATE students SET cycle_start_date=%s WHERE id=%s", (cycle_start, s["id"]), fetch="none")
        
        days_passed = (today - cycle_start).days
        
        # --- Generate bills for any completed 30-day cycles ---
        if days_passed >= 30:
            while days_passed >= 30:
                cycle_end = cycle_start + timedelta(days=29)
                
                existing = query(
                    "SELECT id FROM billing WHERE user_id=%s AND cycle_start=%s",
                    (s["id"], cycle_start), fetch="one"
                )
                if not existing:
                    meal_count, total_bill = calc_bill_for_period(s["id"], cycle_start, cycle_end)
                    query(
                        """INSERT INTO billing (user_id, cycle_start, cycle_end, total_meals, total_bill, status) 
                           VALUES (%s, %s, %s, %s, %s, 'pending')""",
                        (s["id"], cycle_start, cycle_end, meal_count, total_bill), fetch="none"
                    )
                    generated += 1
                
                cycle_start = cycle_start + timedelta(days=30)
                days_passed = (today - cycle_start).days
                
            query("UPDATE students SET cycle_start_date=%s WHERE id=%s", (cycle_start, s["id"]), fetch="none")
        
        # --- Always ensure a current-cycle bill exists (even for new students) ---
        cycle_end_current = min(today, cycle_start + timedelta(days=29))
        existing_current = query(
            "SELECT id FROM billing WHERE user_id=%s AND cycle_start=%s",
            (s["id"], cycle_start), fetch="one"
        )
        if not existing_current:
            meal_count, total_bill = calc_bill_for_period(s["id"], cycle_start, cycle_end_current)
            query(
                """INSERT INTO billing (user_id, cycle_start, cycle_end, total_meals, total_bill, status) 
                   VALUES (%s, %s, %s, %s, %s, 'pending')""",
                (s["id"], cycle_start, cycle_end_current, meal_count, total_bill), fetch="none"
            )
            generated += 1
        else:
            # Update existing current-cycle bill with latest meal count
            meal_count, total_bill = calc_bill_for_period(s["id"], cycle_start, cycle_end_current)
            query(
                "UPDATE billing SET total_meals=%s, total_bill=%s, cycle_end=%s WHERE user_id=%s AND cycle_start=%s",
                (meal_count, total_bill, cycle_end_current, s["id"], cycle_start), fetch="none"
            )
            
    return generated

@billing_bp.route("/auto-update", methods=["GET", "POST"])
@jwt_required()
def auto_update():
    count = run_billing_automation()
    return jsonify({"message": f"Billing automation ran. Generated {count} new bills."})

@billing_bp.route("/generate/<int:sid>", methods=["POST"])
@jwt_required()
def generate_bill_for_student(sid):
    """Force generate bill for a specific student."""
    today = date.today()
    today = date.today()
    s = query("SELECT id, name, cycle_start_date, date_of_joining FROM students WHERE id=%s AND status='active'", (sid,), fetch="one")
    if not s:
        return jsonify({"error": "Student not found or inactive"}), 404

    c_start = s.get("cycle_start_date")
    if not c_start:
        c_start = s.get("date_of_joining") or today
        query("UPDATE students SET cycle_start_date=%s WHERE id=%s", (c_start, sid), fetch="none")

    days_passed = (today - c_start).days
    
    # Generate for current partial cycle too
    cycle_end = min(today, c_start + timedelta(days=29))
    
    existing = query(
        "SELECT id FROM billing WHERE user_id=%s AND cycle_start=%s",
        (sid, c_start), fetch="one"
    )
    if existing:
        # Update existing bill
        meal_count, total_bill = calc_bill_for_period(sid, c_start, cycle_end)
        query(
            "UPDATE billing SET total_meals=%s, total_bill=%s, cycle_end=%s WHERE user_id=%s AND cycle_start=%s",
            (meal_count, total_bill, cycle_end, sid, c_start), fetch="none"
        )
        return jsonify({"message": f"Bill updated for {s['name']}. Meals: {meal_count}, Amount: ₹{total_bill}"})
    else:
        meal_count, total_bill = calc_bill_for_period(sid, c_start, cycle_end)
        query(
            """INSERT INTO billing (user_id, cycle_start, cycle_end, total_meals, total_bill, status) 
               VALUES (%s, %s, %s, %s, %s, 'pending')""",
            (sid, c_start, cycle_end, meal_count, total_bill), fetch="none"
        )
        return jsonify({"message": f"Bill created for {s['name']}. Meals: {meal_count}, Amount: ₹{total_bill}"}), 201

@billing_bp.route("/export/csv", methods=["GET"])
@jwt_required()
def export_all_bills_csv():
    rows = query("SELECT b.*, s.name FROM billing b JOIN students s ON b.user_id=s.id ORDER BY b.cycle_end DESC", fetch="all")
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Bill ID", "Student Name", "Cycle Start", "Cycle End", "Total Meals", "Total Bill (Rs)", "Status"])
    for r in rows:
        w.writerow([
            r["id"], r["name"],
            str(r["cycle_start"]), str(r["cycle_end"]),
            r["total_meals"], float(r["total_bill"]),
            r["status"].upper()
        ])
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=all_bills.csv"})

@billing_bp.route("/active", methods=["GET"])
@jwt_required()
def get_active_dashboard_admin():
    run_billing_automation()
    today = date.today()
    students = query("SELECT id, name, date_of_joining, cycle_start_date FROM students WHERE status='active'", fetch="all")
    
    data = []
    for s in students:
        c_start = s.get("cycle_start_date")
        if not c_start:
            c_start = s.get("date_of_joining") or today
            query("UPDATE students SET cycle_start_date=%s WHERE id=%s", (c_start, s["id"]), fetch="none")
        
        days_passed = (today - c_start).days
        days_remaining = max(0, 30 - days_passed)
        
        meal_count, total_bill = calc_bill_for_period(s["id"], c_start, today)
        
        data.append({
            "id": s["id"],
            "name": s["name"],
            "date_of_joining": str(s["date_of_joining"]),
            "meals_taken": meal_count,
            "total_bill": float(total_bill),
            "days_remaining": days_remaining,
            "ending_soon": days_remaining <= 5
        })
        
    return jsonify(data)

@billing_bp.route("/my-cycle", methods=["GET"])
@jwt_required()
def my_cycle():
    identity = parse_identity(get_jwt_identity())
    uid = identity.get("id")
    
    run_billing_automation(uid)
    today = date.today()
    s = query("SELECT date_of_joining, cycle_start_date FROM students WHERE id=%s", (uid,), fetch="one")
    if not s:
        return jsonify({"error": "User not found"}), 404
        
    c_start = s["cycle_start_date"]
    if not c_start:
        return jsonify({"error": "No billing cycle set"}), 400
        
    days_passed = (today - c_start).days
    days_remaining = max(0, 30 - days_passed)
    
    meal_count, total_bill = calc_bill_for_period(uid, c_start, today)
    
    status = "Active"
    if days_remaining <= 5:
        status = "Ending Soon"
        
    return jsonify({
        "date_of_joining": str(s["date_of_joining"]),
        "cycle_start": str(c_start),
        "days_passed": days_passed,
        "days_remaining": days_remaining,
        "meals_taken": meal_count,
        "current_bill": float(total_bill),
        "status": status
    })

@billing_bp.route("/", methods=["GET"])
@jwt_required()
def get_bills():
    identity = parse_identity(get_jwt_identity())
    uid = identity.get("id")
    is_admin = (identity.get("role") == "admin")
    
    # Always run automation first so all active students have a current-cycle bill
    if is_admin:
        run_billing_automation()
    
    # Month filter (optional)
    month = request.args.get("month", "")  # YYYY-MM
    status_filter = request.args.get("status", "")
    
    if is_admin:
        # Use LEFT JOIN so students without bills still show (shouldn't happen after automation)
        sql = """SELECT b.id, b.user_id, b.cycle_start, b.cycle_end, b.total_meals, 
                        b.total_bill, b.status, b.created_at, s.name 
                 FROM billing b 
                 INNER JOIN students s ON b.user_id = s.id 
                 WHERE s.status = 'active'"""
        params = []
        if month:
            sql += " AND DATE_FORMAT(b.cycle_start, '%%Y-%%m') = %s"
            params.append(month)
        if status_filter:
            sql += " AND b.status=%s"
            params.append(status_filter)
        sql += " ORDER BY s.name ASC, b.cycle_end DESC"
        rows = query(sql, params or None, fetch="all")
    else:
        run_billing_automation(uid)
        sql = """SELECT b.id, b.user_id, b.cycle_start, b.cycle_end, b.total_meals, 
                        b.total_bill, b.status, b.created_at, s.name 
                 FROM billing b 
                 INNER JOIN students s ON b.user_id = s.id 
                 WHERE b.user_id=%s"""
        params = [uid]
        if month:
            sql += " AND DATE_FORMAT(b.cycle_start, '%%Y-%%m') = %s"
            params.append(month)
        sql += " ORDER BY b.cycle_end DESC"
        rows = query(sql, params, fetch="all")
        
    for r in rows:
        r["total_bill"] = float(r["total_bill"]) if r.get("total_bill") is not None else 0.0
        r["total_meals"] = r.get("total_meals") or 0
        r["cycle_start"] = str(r["cycle_start"]) if r.get("cycle_start") else ""
        r["cycle_end"] = str(r["cycle_end"]) if r.get("cycle_end") else ""
        r["created_at"] = str(r["created_at"]) if r.get("created_at") else ""
        r["status"] = r.get("status") or "pending"
        
    return jsonify(rows)

@billing_bp.route("/<int:bid>/pay", methods=["PATCH"])
@jwt_required()
def mark_paid(bid):
    query("UPDATE billing SET status='paid' WHERE id=%s", (bid,), fetch="none")
    return jsonify({"message": "Marked paid"})

@billing_bp.route("/<int:bid>/unpay", methods=["PATCH"])
@jwt_required()
def mark_unpaid(bid):
    query("UPDATE billing SET status='pending' WHERE id=%s", (bid,), fetch="none")
    return jsonify({"message": "Marked as pending"})

@billing_bp.route("/settings", methods=["GET"])
@jwt_required()
def get_settings():
    """Get billing settings."""
    try:
        rows = query("SELECT k, val FROM settings", fetch="all")
        return jsonify({r["k"]: r["val"] for r in rows})
    except Exception:
        return jsonify({"cost_per_meal": "40.00", "mess_name": "MessAdmin Hostel"})

@billing_bp.route("/settings", methods=["POST"])
@jwt_required()
def update_settings():
    """Update billing settings (admin only)."""
    identity = parse_identity(get_jwt_identity())
    if identity.get("role") != "admin":
        return jsonify({"error": "Admin only"}), 403
    
    data = request.get_json()
    for key, val in data.items():
        try:
            existing = query("SELECT k FROM settings WHERE k=%s", (key,), fetch="one")
            if existing:
                query("UPDATE settings SET val=%s WHERE k=%s", (str(val), key), fetch="none")
            else:
                query("INSERT INTO settings (k, val) VALUES (%s, %s)", (key, str(val)), fetch="none")
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"message": "Settings updated successfully"})
