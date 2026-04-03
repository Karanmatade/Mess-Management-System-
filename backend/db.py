import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv

load_dotenv()

db_config = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "mess_management"),
    "charset":  "utf8mb4",
    "autocommit": True,
}

connection_pool = pooling.MySQLConnectionPool(
    pool_name="mess_pool",
    pool_size=10,
    **db_config
)

def get_db():
    """Return a connection from the pool."""
    return connection_pool.get_connection()

def query(sql, params=None, fetch="all"):
    """
    Helper to run a query.
    fetch: 'all' | 'one' | 'none'
    Returns rows as list-of-dicts, single dict, or lastrowid.
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params or ())
        if fetch == "all":
            return cursor.fetchall()
        elif fetch == "one":
            return cursor.fetchone()
        else:
            conn.commit()
            return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()
