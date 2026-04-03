-- =====================================================
-- HOSTEL MESS MANAGEMENT SYSTEM - DATABASE SCHEMA
-- =====================================================
-- Run this in MySQL Workbench or mysql CLI:
--   mysql -u root -p < database.sql

CREATE DATABASE IF NOT EXISTS mess_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE mess_management;

-- =====================================================
-- TABLE: admin
-- =====================================================
CREATE TABLE IF NOT EXISTS admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,  -- bcrypt hashed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLE: students
-- =====================================================
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    room_no VARCHAR(10) NOT NULL,
    phone VARCHAR(15),
    email VARCHAR(100),
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLE: attendance
-- =====================================================
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    date DATE NOT NULL,
    breakfast BOOLEAN DEFAULT FALSE,
    lunch BOOLEAN DEFAULT FALSE,
    dinner BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE KEY unique_attendance (student_id, date)
);

-- =====================================================
-- TABLE: menu
-- =====================================================
CREATE TABLE IF NOT EXISTS menu (
    id INT AUTO_INCREMENT PRIMARY KEY,
    day ENUM('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday') NOT NULL UNIQUE,
    breakfast TEXT,
    lunch TEXT,
    dinner TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLE: billing
-- =====================================================
CREATE TABLE IF NOT EXISTS billing (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    month VARCHAR(7) NOT NULL,   -- Format: YYYY-MM
    total_meals INT DEFAULT 0,
    cost_per_meal DECIMAL(8,2) DEFAULT 60.00,
    total_amount DECIMAL(10,2) DEFAULT 0.00,
    payment_status ENUM('paid', 'pending') DEFAULT 'pending',
    payment_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE KEY unique_bill (student_id, month)
);

-- =====================================================
-- SEED DATA
-- =====================================================

-- Admin (password: admin@123)
INSERT INTO admin (username, password) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LQ1eLO8SI5Wd3Xp.p5QvU1W3ZLAFWk5tO8W9a');

-- Students
INSERT INTO students (name, room_no, phone, email, status) VALUES
('Aarav Sharma',      'A-101', '9876543210', 'aarav@example.com',   'active'),
('Priya Patel',       'A-102', '9876543211', 'priya@example.com',   'active'),
('Rohit Verma',       'B-201', '9876543212', 'rohit@example.com',   'active'),
('Ananya Singh',      'B-202', '9876543213', 'ananya@example.com',  'active'),
('Karan Mehta',       'C-301', '9876543214', 'karan@example.com',   'active'),
('Sneha Gupta',       'C-302', '9876543215', 'sneha@example.com',   'active'),
('Amit Kumar',        'D-401', '9876543216', 'amit@example.com',    'active'),
('Pooja Yadav',       'D-402', '9876543217', 'pooja@example.com',   'active'),
('Vikram Joshi',      'A-103', '9876543218', 'vikram@example.com',  'inactive'),
('Ritika Agarwal',    'B-203', '9876543219', 'ritika@example.com',  'active');

-- Weekly Menu
INSERT INTO menu (day, breakfast, lunch, dinner) VALUES
('Monday',    'Poha, Chai, Banana',                    'Dal Tadka, Roti, Rice, Sabzi, Salad',    'Paneer Butter Masala, Naan, Rice, Raita'),
('Tuesday',   'Idli Sambar, Coconut Chutney, Chai',    'Rajma Chawal, Papad, Salad',             'Dal Makhani, Roti, Jeera Rice, Pickle'),
('Wednesday', 'Paratha, Curd, Pickle, Chai',           'Chole Bhature, Lassi',                   'Aloo Matar, Roti, Rice, Salad'),
('Thursday',  'Upma, Chutney, Chai',                   'Mix Veg, Roti, Rice, Dal',               'Shahi Paneer, Paratha, Kheer'),
('Friday',    'Aloo Puri, Chai',                       'Kadhi Chawal, Sabzi, Papad',             'Dal Fry, Roti, Rice, Raita'),
('Saturday',  'Bread Butter, Jam, Chai, Boiled Egg',   'Egg Curry / Paneer Curry, Rice, Roti',   'Biryani, Raita, Papad, Salad'),
('Sunday',    'Chole Bhature, Lassi',                  'Special Thali (Dal, Rice, 3 Sabzi, Roti, Sweet)', 'Fried Rice, Manchurian, Papad');

-- Attendance (last 7 days for sample students)
INSERT INTO attendance (student_id, date, breakfast, lunch, dinner) VALUES
(1, CURDATE() - INTERVAL 6 DAY, 1, 1, 1),
(1, CURDATE() - INTERVAL 5 DAY, 1, 0, 1),
(1, CURDATE() - INTERVAL 4 DAY, 1, 1, 1),
(1, CURDATE() - INTERVAL 3 DAY, 0, 1, 1),
(1, CURDATE() - INTERVAL 2 DAY, 1, 1, 0),
(1, CURDATE() - INTERVAL 1 DAY, 1, 1, 1),
(2, CURDATE() - INTERVAL 6 DAY, 0, 1, 1),
(2, CURDATE() - INTERVAL 5 DAY, 1, 1, 1),
(2, CURDATE() - INTERVAL 4 DAY, 1, 0, 1),
(2, CURDATE() - INTERVAL 3 DAY, 1, 1, 1),
(2, CURDATE() - INTERVAL 2 DAY, 0, 1, 1),
(2, CURDATE() - INTERVAL 1 DAY, 1, 1, 0),
(3, CURDATE() - INTERVAL 6 DAY, 1, 1, 1),
(3, CURDATE() - INTERVAL 5 DAY, 1, 1, 1),
(3, CURDATE() - INTERVAL 4 DAY, 0, 0, 1),
(3, CURDATE() - INTERVAL 3 DAY, 1, 1, 1),
(4, CURDATE() - INTERVAL 6 DAY, 1, 1, 1),
(4, CURDATE() - INTERVAL 5 DAY, 1, 1, 1),
(5, CURDATE() - INTERVAL 6 DAY, 1, 0, 1),
(5, CURDATE() - INTERVAL 5 DAY, 1, 1, 1),
(5, CURDATE() - INTERVAL 4 DAY, 1, 1, 0),
(6, CURDATE() - INTERVAL 6 DAY, 0, 1, 1),
(6, CURDATE() - INTERVAL 5 DAY, 1, 1, 1);

-- Billing for current month
INSERT INTO billing (student_id, month, total_meals, cost_per_meal, total_amount, payment_status) VALUES
(1, DATE_FORMAT(CURDATE(), '%Y-%m'), 54, 60.00, 3240.00, 'paid'),
(2, DATE_FORMAT(CURDATE(), '%Y-%m'), 52, 60.00, 3120.00, 'pending'),
(3, DATE_FORMAT(CURDATE(), '%Y-%m'), 48, 60.00, 2880.00, 'paid'),
(4, DATE_FORMAT(CURDATE(), '%Y-%m'), 60, 60.00, 3600.00, 'pending'),
(5, DATE_FORMAT(CURDATE(), '%Y-%m'), 45, 60.00, 2700.00, 'paid'),
(6, DATE_FORMAT(CURDATE(), '%Y-%m'), 58, 60.00, 3480.00, 'pending'),
(7, DATE_FORMAT(CURDATE(), '%Y-%m'), 55, 60.00, 3300.00, 'paid'),
(8, DATE_FORMAT(CURDATE(), '%Y-%m'), 50, 60.00, 3000.00, 'pending');
