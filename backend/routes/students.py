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
    sql += " ORDER BY name"
    rows = query(sql, params or None, fetch="all")
    for s in rows:
        s["created_at"]   = str(s["created_at"])
        s["join_date"]    = str(s["join_date"]) if s.get("join_date") else str(s["created_at"])[:10]
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
    if not d.get("name") or not d.get("room_no"):
        return jsonify({"error": "name and room_no required"}), 400
    new_id = query(
        "INSERT INTO students (name,room_no,phone,parent_phone,email,status,monthly_fee,join_date) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
        (d["name"],d["room_no"],d.get("phone",""),d.get("parent_phone",""),d.get("email",""),
         d.get("status","active"),float(d.get("monthly_fee",1800)), d.get("join_date", date.today().isoformat())),
        fetch="none"
    )
    return jsonify({"message":"Student added","id":new_id}), 201

@students_bp.route("/<int:sid>", methods=["PUT"])
@jwt_required()
def update_student(sid):
    d = request.get_json()
    query(
        "UPDATE students SET name=%s,room_no=%s,phone=%s,parent_phone=%s,email=%s,status=%s,monthly_fee=%s,join_date=%s WHERE id=%s",
        (d["name"],d["room_no"],d.get("phone",""),d.get("parent_phone",""),d.get("email",""),
         d.get("status","active"),float(d.get("monthly_fee",1800)),d.get("join_date", date.today().isoformat()),sid),
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
@students_bp.route("/export/csv", methods=["GET"])
@jwt_required()
def export_all_csv():
    rows = query("SELECT * FROM students ORDER BY name", fetch="all")
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["ID","Name","Room No","Phone","Parent Phone","Email","Status","Monthly Fee (₹)","Joined (Date)"])
    for r in rows:
        w.writerow([r["id"],r["name"],r["room_no"],r.get("phone",""),r.get("parent_phone",""),
                    r.get("email",""),r["status"],
                    float(r.get("monthly_fee") or 1800),
                    str(r.get("join_date") or r["created_at"])[:10]])
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition":"attachment;filename=all_students.csv"})

@students_bp.route("/<int:sid>/export/csv", methods=["GET"])
@jwt_required()
def export_student_csv(sid):
    s = query("SELECT * FROM students WHERE id=%s",(sid,),fetch="one")
    if not s: return jsonify({"error":"Not found"}),404

    att = query(
        "SELECT date,breakfast,lunch,dinner FROM attendance WHERE student_id=%s ORDER BY date DESC LIMIT 60",
        (sid,), fetch="all"
    )
    bills = query(
        "SELECT month,total_meals,cost_per_meal,total_amount,paid_amount,payment_status FROM billing WHERE student_id=%s ORDER BY month DESC",
        (sid,), fetch="all"
    )

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["=== STUDENT DETAILS ==="])
    w.writerow(["Name",s["name"]]); w.writerow(["Room",s["room_no"]])
    w.writerow(["Phone",s.get("phone","")]); w.writerow(["Parent Phone",s.get("parent_phone","")])
    w.writerow(["Email",s.get("email","")]); w.writerow(["Join Date",str(s.get("join_date") or s["created_at"])[:10]])
    w.writerow(["Status",s["status"]]); w.writerow(["Monthly Fee",float(s.get("monthly_fee") or 1800)])
    w.writerow([])
    w.writerow(["=== BILLING HISTORY ==="])
    w.writerow(["Month","Total Meals","Rate/Meal","Amount","Paid","Status"])
    for b in bills:
        w.writerow([b["month"],b["total_meals"],float(b["cost_per_meal"]),
                    float(b["total_amount"]),float(b.get("paid_amount") or 0),b["payment_status"]])
    w.writerow([])
    w.writerow(["=== ATTENDANCE (LAST 60 DAYS) ==="])
    w.writerow(["Date","Breakfast","Lunch","Dinner","Total"])
    for a in att:
        total = (1 if a["breakfast"] else 0)+(1 if a["lunch"] else 0)+(1 if a["dinner"] else 0)
        w.writerow([str(a["date"]),"Yes" if a["breakfast"] else "No",
                    "Yes" if a["lunch"] else "No","Yes" if a["dinner"] else "No",total])

    fname = f"{s['name'].replace(' ','_')}_report.csv"
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition":f"attachment;filename={fname}"})
