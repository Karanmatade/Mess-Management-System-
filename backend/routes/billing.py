from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from db import query
from datetime import date

billing_bp = Blueprint("billing", __name__)

COST_PER_MEAL = 60.00

@billing_bp.route("/", methods=["GET"])
@jwt_required()
def get_bills():
    month  = request.args.get("month", date.today().strftime("%Y-%m"))
    status = request.args.get("status")
    sql = """SELECT b.*, s.name, s.room_no, s.monthly_fee
             FROM billing b JOIN students s ON b.student_id=s.id
             WHERE b.month=%s"""
    params = [month]
    if status:
        sql += " AND b.payment_status=%s"; params.append(status)
    sql += " ORDER BY s.name"
    rows = query(sql, params, fetch="all")
    for r in rows:
        r["total_amount"]   = float(r["total_amount"])
        r["cost_per_meal"]  = float(r["cost_per_meal"])
        r["paid_amount"]    = float(r.get("paid_amount") or 0)
        r["advance_amount"] = float(r.get("advance_amount") or 0)
        r["monthly_fee"]    = float(r.get("monthly_fee") or 1800)
        r["payment_date"]   = str(r["payment_date"]) if r["payment_date"] else None
        r["created_at"]     = str(r["created_at"])
        r["balance"]        = round(r["total_amount"] - r["paid_amount"], 2)
    return jsonify(rows)

@billing_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_bills():
    d     = request.get_json() or {}
    month = d.get("month", date.today().strftime("%Y-%m"))
    cost  = float(d.get("cost_per_meal", COST_PER_MEAL))
    students = query("SELECT id FROM students WHERE status='active'", fetch="all")
    generated = 0
    for s in students:
        sid = s["id"]
        row = query(
            "SELECT COALESCE(SUM(breakfast+lunch+dinner),0) AS tm FROM attendance WHERE student_id=%s AND date LIKE %s",
            (sid, month + "-%"), fetch="one"
        )
        tm  = int(row["tm"])
        amt = round(tm * cost, 2)
        query(
            """INSERT INTO billing (student_id,month,total_meals,cost_per_meal,total_amount)
               VALUES(%s,%s,%s,%s,%s)
               ON DUPLICATE KEY UPDATE total_meals=%s,cost_per_meal=%s,total_amount=%s""",
            (sid,month,tm,cost,amt, tm,cost,amt), fetch="none"
        )
        generated += 1
    return jsonify({"message":f"Bills generated for {generated} students","month":month})

@billing_bp.route("/<int:bid>", methods=["PUT"])
@jwt_required()
def edit_bill(bid):
    """Edit cost_per_meal, recalculate total, record payment."""
    d = request.get_json()
    bill = query("SELECT * FROM billing WHERE id=%s",(bid,),fetch="one")
    if not bill: return jsonify({"error":"Not found"}),404

    cost = float(d.get("cost_per_meal", bill["cost_per_meal"]))
    tm   = int(d.get("total_meals", bill["total_meals"]))
    total= round(tm * cost, 2)
    paid = float(d.get("paid_amount", bill.get("paid_amount") or 0))
    advance = max(0, round(paid - total, 2))
    status  = d.get("payment_status",
                    "paid" if paid >= total else ("pending" if paid == 0 else "partial"))

    query(
        """UPDATE billing SET cost_per_meal=%s,total_meals=%s,total_amount=%s,
           paid_amount=%s,advance_amount=%s,payment_status=%s,
           payment_date=IF(%s>0,CURDATE(),payment_date)
           WHERE id=%s""",
        (cost,tm,total,paid,advance,status,paid,bid), fetch="none"
    )
    return jsonify({"message":"Bill updated","balance":round(total-paid,2),"advance":advance})

@billing_bp.route("/<int:bid>/pay", methods=["PATCH"])
@jwt_required()
def mark_paid(bid):
    bill = query("SELECT total_amount FROM billing WHERE id=%s",(bid,),fetch="one")
    if not bill: return jsonify({"error":"Not found"}),404
    query("UPDATE billing SET payment_status='paid',paid_amount=total_amount,payment_date=CURDATE() WHERE id=%s",(bid,),fetch="none")
    return jsonify({"message":"Marked paid"})

@billing_bp.route("/<int:bid>/unpay", methods=["PATCH"])
@jwt_required()
def mark_unpaid(bid):
    query("UPDATE billing SET payment_status='pending',paid_amount=0,payment_date=NULL WHERE id=%s",(bid,),fetch="none")
    return jsonify({"message":"Marked pending"})

@billing_bp.route("/student/<int:sid>", methods=["GET"])
@jwt_required()
def student_bills(sid):
    rows = query("SELECT * FROM billing WHERE student_id=%s ORDER BY month DESC",(sid,),fetch="all")
    for r in rows:
        r["total_amount"]   = float(r["total_amount"])
        r["cost_per_meal"]  = float(r["cost_per_meal"])
        r["paid_amount"]    = float(r.get("paid_amount") or 0)
        r["advance_amount"] = float(r.get("advance_amount") or 0)
        r["payment_date"]   = str(r["payment_date"]) if r["payment_date"] else None
        r["created_at"]     = str(r["created_at"])
    return jsonify(rows)
