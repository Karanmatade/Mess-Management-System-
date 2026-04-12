"""Test billing automation - creates bills for all students"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from db import query
from routes.billing import run_billing_automation
import json, datetime

def fix(o):
    if isinstance(o, (datetime.date, datetime.datetime)): return str(o)
    return str(o)

print("Running billing automation...")
count = run_billing_automation()
print(f"Generated/Updated: {count} bills")

print("\n=== ALL BILLING ROWS ===")
rows = query("SELECT b.id, b.user_id, b.cycle_start, b.cycle_end, b.total_meals, b.total_bill, b.status, s.name FROM billing b JOIN students s ON b.user_id=s.id WHERE s.status='active' ORDER BY s.name", fetch='all')
for r in rows:
    print(f"  Bill #{r['id']}: {r['name']} | {r['cycle_start']} -> {r['cycle_end']} | Meals:{r['total_meals']} | Rs{r['total_bill']} | {r['status']}")

print(f"\nTotal: {len(rows)} billing records for active students")

# Check students without any billing record
students = query("SELECT id, name FROM students WHERE status='active'", fetch='all')
billed_ids = set(r['user_id'] for r in rows)
unbilled = [s for s in students if s['id'] not in billed_ids]
if unbilled:
    print(f"\nWARNING: {len(unbilled)} students still without bills: {[s['name'] for s in unbilled]}")
else:
    print("\n✅ All active students have billing records!")
