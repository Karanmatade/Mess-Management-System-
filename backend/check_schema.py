from db import query
import json, datetime

def fix(o):
    if isinstance(o, (datetime.date, datetime.datetime)): return str(o)
    return str(o)

billing = query('SELECT id, user_id, cycle_start, cycle_end, status FROM billing', fetch='all')
students = query('SELECT id, name, status, date_of_joining, cycle_start_date FROM students', fetch='all')

with open('diag_result.json', 'w', encoding='utf-8') as f:
    json.dump({'billing': billing, 'students': students}, f, default=fix, indent=2)

print("Written to diag_result.json")
print(f"Billing rows: {len(billing)}")
print(f"Student rows: {len(students)}")
