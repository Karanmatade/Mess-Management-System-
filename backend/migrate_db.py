"""
Migration script — run this from the backend folder:
  python migrate_db.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from db import query

def run(sql, ignore_errors=True):
    try:
        query(sql, fetch="none")
        print(f"  ✅  OK")
    except Exception as e:
        if ignore_errors:
            print(f"  ⚠️  Skipped ({e})")
        else:
            raise

steps = [
    # students extra columns
    ("ADD   students.password",           "ALTER TABLE students ADD COLUMN password VARCHAR(255) DEFAULT NULL"),
    ("ADD   students.email",              "ALTER TABLE students ADD COLUMN email VARCHAR(100) DEFAULT NULL"),
    ("ADD   students.parent_phone",       "ALTER TABLE students ADD COLUMN parent_phone VARCHAR(15) DEFAULT NULL"),
    ("ADD   students.date_of_joining",    "ALTER TABLE students ADD COLUMN date_of_joining DATE DEFAULT NULL"),
    ("ADD   students.cycle_start_date",   "ALTER TABLE students ADD COLUMN cycle_start_date DATE DEFAULT NULL"),
    ("ADD   students.monthly_fee",        "ALTER TABLE students ADD COLUMN monthly_fee DECIMAL(8,2) DEFAULT 1800.00"),

    # meals table
    ("CREATE meals",
     """CREATE TABLE IF NOT EXISTS meals (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        date DATE NOT NULL,
        meal_type ENUM('Breakfast','Lunch','Dinner') NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES students(id) ON DELETE CASCADE,
        UNIQUE KEY unique_meal (user_id, date, meal_type)
     )"""),

    # billing table (new cycle-based schema)
    ("CREATE billing",
     """CREATE TABLE IF NOT EXISTS billing (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        cycle_start DATE NOT NULL,
        cycle_end DATE NOT NULL,
        total_meals INT DEFAULT 0,
        total_bill DECIMAL(10,2) DEFAULT 0.00,
        status ENUM('paid','pending') DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES students(id) ON DELETE CASCADE
     )"""),

    # settings table
    ("CREATE settings",
     """CREATE TABLE IF NOT EXISTS settings (
        k VARCHAR(100) PRIMARY KEY,
        val TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
     )"""),

    # seed settings
    ("SEED cost_per_meal",  "INSERT IGNORE INTO settings (k,val) VALUES ('cost_per_meal','40.00')"),
    ("SEED mess_name",      "INSERT IGNORE INTO settings (k,val) VALUES ('mess_name','MessAdmin Hostel')"),
    ("SEED owner_name",     "INSERT IGNORE INTO settings (k,val) VALUES ('owner_name','Mess Owner')"),
    ("SEED contact_phone",  "INSERT IGNORE INTO settings (k,val) VALUES ('contact_phone','')"),
    ("SEED address",        "INSERT IGNORE INTO settings (k,val) VALUES ('address','')"),
    ("SEED default_fee",    "INSERT IGNORE INTO settings (k,val) VALUES ('default_fee','1800')"),
    ("SEED late_note",      "INSERT IGNORE INTO settings (k,val) VALUES ('late_note','Please pay by the 5th of next month')"),
    ("SEED alert_days",     "INSERT IGNORE INTO settings (k,val) VALUES ('alert_days','5')"),

    # seed admin
    ("SEED admin",
     "INSERT IGNORE INTO admin (username,password) VALUES ('admin','$2b$12$LQv3c1yqBWVHxkd0LQ1eLO8SI5Wd3Xp.p5QvU1W3ZLAFWk5tO8W9a')"),

    # fix students with null date_of_joining
    ("FIX  date_of_joining",
     "UPDATE students SET date_of_joining=DATE(created_at) WHERE date_of_joining IS NULL"),
    ("FIX  cycle_start_date",
     "UPDATE students SET cycle_start_date=date_of_joining WHERE cycle_start_date IS NULL AND date_of_joining IS NOT NULL"),
]

print("\n🚀  Running Mess Management DB Migration...\n")
for label, sql in steps:
    print(f"  ▶  {label}")
    run(sql)

print("\n✅  Migration complete!\n")
