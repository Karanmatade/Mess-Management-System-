from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required
from db import query
from datetime import date
import csv, io

students_bp = Blueprint("students", __name__)

@students_bp.route("/", methods=["GET"])
@jwt_required()
def get_students():
    status = request.args.get("status")
    search = request.args.get("search", "").strip()
    sql = "SELECT * FROM students WHERE 1=1"
    params = []
    if status:
        sql += " AND status=%s"; params.append(status)
    if search:
        like = f"%{search}%"
        sql += " AND (name LIKE %s OR room_no LIKE %s OR email LIKE %s OR phone LIKE %s)"
        params.extend([like, like, like, like])
    sql += " ORDER BY id ASC"
    rows = query(sql, params or None, fetch="all")
    for s in rows:
        s["created_at"]   = str(s["created_at"])
        s["join_date"]    = str(s.get("date_of_joining") or s.get("join_date") or str(s["created_at"])[:10])
        s["monthly_fee"]  = float(s.get("monthly_fee") or 1800)
    return jsonify(rows)

@students_bp.route("/<int:sid>", methods=["GET"])
@jwt_required()
def get_student(sid):
    s = query("SELECT * FROM students WHERE id=%s", (sid,), fetch="one")
    if not s: return jsonify({"error": "Not found"}), 404
    s["created_at"]  = str(s["created_at"])
    s["join_date"]   = str(s["join_date"]) if s.get("join_date") else str(s["created_at"])[:10]
    s["monthly_fee"] = float(s.get("monthly_fee") or 1800)
    return jsonify(s)

@students_bp.route("/", methods=["POST"])
@jwt_required()
def add_student():
    d = request.get_json()
    if not d.get("name") or not d.get("email") or not d.get("date_of_joining"):
        return jsonify({"error": "name, email and date_of_joining required"}), 400
        
    password = d.get("password") or "12345"
    from routes.auth import bcrypt
    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    
    new_id = query(
        "INSERT INTO students (name,room_no,phone,email,password,status,date_of_joining,cycle_start_date) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
        (d["name"],d.get("room_no", "N/A"),d.get("phone",""),d["email"],hashed,
         d.get("status","active"),d["date_of_joining"],d["date_of_joining"]),
        fetch="none"
    )
    return jsonify({"message":"Student added","id":new_id}), 201

@students_bp.route("/<int:sid>", methods=["PUT"])
@jwt_required()
def update_student(sid):
    d = request.get_json()
    # Try to update parent_phone and monthly_fee too (columns may exist)
    try:
        query(
            "UPDATE students SET name=%s, room_no=%s, phone=%s, parent_phone=%s, email=%s, monthly_fee=%s, status=%s WHERE id=%s",
            (d["name"], d["room_no"], d.get("phone",""), d.get("parent_phone",""),
             d.get("email",""), d.get("monthly_fee", 1800), d.get("status","active"), sid),
            fetch="none"
        )
    except Exception:
        query(
            "UPDATE students SET name=%s, room_no=%s, phone=%s, email=%s, status=%s WHERE id=%s",
            (d["name"], d["room_no"], d.get("phone",""), d.get("email",""), d.get("status","active"), sid),
            fetch="none"
        )
    return jsonify({"message":"Updated"})

@students_bp.route("/<int:sid>", methods=["DELETE"])
@jwt_required()
def delete_student(sid):
    if not query("SELECT id FROM students WHERE id=%s",(sid,),fetch="one"):
        return jsonify({"error":"Not found"}),404
    query("DELETE FROM students WHERE id=%s",(sid,),fetch="none")
    return jsonify({"message":"Deleted"})

@students_bp.route("/<int:sid>/toggle-status", methods=["PATCH"])
@jwt_required()
def toggle_status(sid):
    s = query("SELECT status FROM students WHERE id=%s",(sid,),fetch="one")
    if not s: return jsonify({"error":"Not found"}),404
    ns = "inactive" if s["status"]=="active" else "active"
    query("UPDATE students SET status=%s WHERE id=%s",(ns,sid),fetch="none")
    return jsonify({"status":ns})

# ── CSV exports ────────────────────────────────────────────────
def fmt_date(val):
    """Format a date/datetime/string value as an Excel text formula to avoid ########."""
    if not val:
        return ""
    import datetime
    if isinstance(val, (datetime.date, datetime.datetime)):
        d_str = val.strftime("%d-%b-%Y") # e.g. 05-Apr-2026
    else:
        s = str(val)[:10]
        try:
            d_str = datetime.datetime.strptime(s, "%Y-%m-%d").strftime("%d-%b-%Y")
        except Exception:
            d_str = s
    return f'="{d_str}"'  # Forces Excel to show it as text exactly as is

def fmt_phone(val):
    """Format phone as an Excel text formula to avoid scientific notation (8.4E+09)."""
    if not val:
        return ""
    # Strip whitespace/newlines just in case
    clean_val = str(val).strip()
    return f'="{clean_val}"'

@students_bp.route("/export/csv", methods=["GET"])
@jwt_required()
def export_all_csv():
    rows = query("SELECT * FROM students ORDER BY id ASC", fetch="all")
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["ID", "Name", "Room No", "Phone", "Email",
                "Monthly Fee", "Status", "Joined Date"])
    for r in rows:
        w.writerow([
            r["id"],
            r["name"],
            r["room_no"],
            fmt_phone(r.get("phone", "")),
            r.get("email", ""),
            r.get("monthly_fee", ""),
            r["status"],
            fmt_date(r.get("date_of_joining") or r.get("created_at"))
        ])
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=all_students.csv"})

@students_bp.route("/<int:sid>/export/csv", methods=["GET"])
@jwt_required()
def export_student_csv(sid):
    s = query("SELECT * FROM students WHERE id=%s",(sid,),fetch="one")
    if not s: return jsonify({"error":"Not found"}),404

    att = query(
        "SELECT date, meal_type FROM meals WHERE user_id=%s ORDER BY date DESC LIMIT 60",
        (sid,), fetch="all"
    )
    bills = query(
        "SELECT cycle_start, cycle_end, total_meals, total_bill, status FROM billing WHERE user_id=%s ORDER BY cycle_end DESC",
        (sid,), fetch="all"
    )

    buf = io.StringIO()
    w = csv.writer(buf)
    # ── Student Details block ──────────────────────────
    w.writerow(["=== STUDENT DETAILS ==="])
    w.writerow(["Name",          s["name"]])
    w.writerow(["Room",          s["room_no"]])
    w.writerow(["Phone",         fmt_phone(s.get("phone", ""))])
    w.writerow(["Parent Phone",  fmt_phone(s.get("parent_phone", ""))])
    w.writerow(["Email",         s.get("email", "")])
    w.writerow(["Monthly Fee",   s.get("monthly_fee", "")])
    w.writerow(["Join Date",     fmt_date(s.get("date_of_joining") or s.get("created_at"))])
    w.writerow(["Status",        s["status"]])
    w.writerow([])
    # ── Billing History block ──────────────────────────
    w.writerow(["=== BILLING HISTORY ==="])
    w.writerow(["Cycle Start", "Cycle End", "Total Meals", "Amount (Rs)", "Status"])
    for b in bills:
        w.writerow([
            fmt_date(b["cycle_start"]),
            fmt_date(b["cycle_end"]),
            b["total_meals"],
            float(b["total_bill"]),
            b["status"]
        ])
    w.writerow([])
    # ── Meals block ────────────────────────────────────
    w.writerow(["=== MEALS (LAST 60 ENTRIES) ==="])
    w.writerow(["Date", "Meal Type"])
    for a in att:
        w.writerow([fmt_date(a["date"]), a["meal_type"]])

    fname = f"{s['name'].replace(' ', '_')}_report.csv"
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment;filename={fname}"})
