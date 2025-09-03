# inspect_db.py
import sqlite3

# Connect to our timetable.db
conn = sqlite3.connect("timetable.db")

# Ask SQLite: "What tables do you have?"
tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table';"
).fetchall()

print("📋 Tables in timetable.db:", tables)

# For each table, print its schema
for (table_name,) in tables:
    print(f"\n🔎 Schema for table: {table_name}")
    schema = conn.execute(f"PRAGMA table_info({table_name});").fetchall()
    for col in schema:
        print(f"   - {col}")

conn.close()
