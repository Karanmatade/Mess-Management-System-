from db import get_db

conn = get_db()
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE students ADD COLUMN password VARCHAR(255) DEFAULT '';")
    cursor.execute("ALTER TABLE students ADD COLUMN date_of_joining DATE;")
    cursor.execute("ALTER TABLE students ADD COLUMN cycle_start_date DATE;")
except Exception as e:
    print(e) # Ignore if exists

try:
    cursor.execute("UPDATE students SET date_of_joining=DATE(created_at), cycle_start_date=DATE(created_at) WHERE date_of_joining IS NULL;")
except Exception as e:
    pass

cursor.execute("""
CREATE TABLE IF NOT EXISTS meals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    date DATE NOT NULL,
    meal_type ENUM('Breakfast', 'Lunch', 'Dinner') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE KEY uq_meal_entry (user_id, date, meal_type)
);
""")

cursor.execute("DROP TABLE IF EXISTS billing;")
cursor.execute("""
CREATE TABLE billing (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    cycle_start DATE NOT NULL,
    cycle_end DATE NOT NULL,
    total_meals INT DEFAULT 0,
    total_bill DECIMAL(10,2) DEFAULT 0.00,
    status ENUM('paid', 'pending') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES students(id) ON DELETE CASCADE
);
""")

# Convert old attendance table to new meals table for existing data
try:
    cursor.execute("SELECT student_id, date, breakfast, lunch, dinner FROM attendance")
    rows = cursor.fetchall()
    for r in rows:
        uid, dt, b, l, d = r
        if b:
            cursor.execute("INSERT IGNORE INTO meals (user_id, date, meal_type) VALUES (%s, %s, 'Breakfast')", (uid, dt))
        if l:
            cursor.execute("INSERT IGNORE INTO meals (user_id, date, meal_type) VALUES (%s, %s, 'Lunch')", (uid, dt))
        if d:
            cursor.execute("INSERT IGNORE INTO meals (user_id, date, meal_type) VALUES (%s, %s, 'Dinner')", (uid, dt))
except Exception as e:
    print("Migration error:", e)

conn.commit()
print("Database schema successfully upgraded to Smart Automated Billing.")
