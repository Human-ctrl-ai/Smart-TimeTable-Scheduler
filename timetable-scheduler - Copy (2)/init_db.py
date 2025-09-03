# init_db.py
from app import app, db
from app import Classroom  # 👈 import the model explicitly

# Create tables inside app context
with app.app_context():
    db.create_all()
    print("✅ Tables created successfully in timetable.db")
