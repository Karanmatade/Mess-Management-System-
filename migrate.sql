-- =====================================================
-- MIGRATION: Add missing columns & settings table
-- Run this once after the initial setup if needed
-- =====================================================

USE mess_management;

-- ── Add missing columns to students table ────────────
ALTER TABLE students
  ADD COLUMN IF NOT EXISTS password VARCHAR(255) DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS email VARCHAR(100) DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS parent_phone VARCHAR(15) DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS date_of_joining DATE DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS cycle_start_date DATE DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS monthly_fee DECIMAL(8,2) DEFAULT 1800.00;

-- ── Create the NEW billing table (cycle-based) ────────
-- Drop old billing table if it uses old schema (student_id/month/payment_status)
-- WARNING: Only run if you are starting fresh or have backed up old billing data
-- DROP TABLE IF EXISTS billing;

CREATE TABLE IF NOT EXISTS billing (
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

-- ── Create meals table (used instead of old attendance) ─
CREATE TABLE IF NOT EXISTS meals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    date DATE NOT NULL,
    meal_type ENUM('Breakfast', 'Lunch', 'Dinner') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE KEY unique_meal (user_id, date, meal_type)
);

-- ── Create settings table ─────────────────────────────
CREATE TABLE IF NOT EXISTS settings (
    k VARCHAR(100) PRIMARY KEY,
    val TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ── Seed default settings ─────────────────────────────
INSERT IGNORE INTO settings (k, val) VALUES
('cost_per_meal',  '40.00'),
('mess_name',      'MessAdmin Hostel'),
('owner_name',     'Mess Owner'),
('contact_phone',  ''),
('address',        ''),
('default_fee',    '1800'),
('late_note',      'Please pay by the 5th of next month'),
('alert_days',     '5');

-- ── Ensure admin exists (password: admin@123) ─────────
INSERT IGNORE INTO admin (username, password) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LQ1eLO8SI5Wd3Xp.p5QvU1W3ZLAFWk5tO8W9a');

-- ── Update students with date_of_joining if null ──────
UPDATE students
SET date_of_joining = DATE(created_at),
    cycle_start_date = DATE(created_at)
WHERE date_of_joining IS NULL;
