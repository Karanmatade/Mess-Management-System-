import db

new_students = [
    ('Ravi Shankar', 'D-501', '9876543220', 'ravi@example.com', 'active'),
    ('Siddharth Roy', 'D-502', '9876543221', 'siddharth@example.com', 'active'),
    ('Neha Sharma', 'E-101', '9876543222', 'neha@example.com', 'active'),
    ('Rajesh Kumar', 'E-102', '9876543223', 'rajesh@example.com', 'active'),
    ('Aditi Desai', 'E-201', '9876543224', 'aditi@example.com', 'active'),
    ('Arjun Reddy', 'E-202', '9876543225', 'arjun@example.com', 'active'),
    ('Priyanka Chopra', 'F-301', '9876543226', 'priyanka@example.com', 'active'),
    ('Deepak Singh', 'F-302', '9876543227', 'deepak@example.com', 'active'),
    ('Shreya Ghoshal', 'G-401', '9876543228', 'shreya@example.com', 'active'),
    ('Manish Pandey', 'G-402', '9876543229', 'manish@example.com', 'active')
]

for student in new_students:
    db.query('''
        INSERT INTO students (name, room_no, phone, email, status) 
        VALUES (%s, %s, %s, %s, %s)
    ''', student, fetch="none")

print("Successfully added 10 new members!")
