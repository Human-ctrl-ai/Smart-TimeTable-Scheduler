import sqlite3

# connect to our database file
conn = sqlite3.connect("timetable.db")

# ask SQLite to list all tables
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()

print("Tables in timetable.db:", tables)

conn.close()
