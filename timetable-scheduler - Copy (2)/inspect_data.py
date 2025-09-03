import sqlite3

# Connect to the database
conn = sqlite3.connect("timetable.db")
cursor = conn.cursor()

# Fetch all classrooms
cursor.execute("SELECT * FROM classroom;")
rows = cursor.fetchall()

print("📊 Classroom Records:")
for row in rows:
    print(row)

conn.close()
