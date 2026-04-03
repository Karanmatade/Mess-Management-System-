import sys
sys.path.insert(0, '.')
from flask_bcrypt import Bcrypt
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

b = Bcrypt()
hashed = b.generate_password_hash('admin@123').decode('utf-8')
print("Generated hash:", hashed)

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST","localhost"),
    user=os.getenv("DB_USER","root"),
    password=os.getenv("DB_PASSWORD",""),
    database=os.getenv("DB_NAME","mess_management")
)
cursor = conn.cursor()
cursor.execute("UPDATE admin SET password=%s WHERE username='admin'", (hashed,))
conn.commit()
print("Password updated successfully!")
print("Rows affected:", cursor.rowcount)
cursor.close()
conn.close()
