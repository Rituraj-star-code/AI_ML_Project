
import sqlite3
from database import DB_PATH, init_db

# Initialize database
init_db()

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check available tables
cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
""")

tables = cursor.fetchall()

print("Available tables:")

for table in tables:
    print(table[0])

conn.close()
