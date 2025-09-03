# config.py
import os

# Secret key for sessions & security (replace with something stronger in production!)
SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-key-change-this")

# Optional: Central place to keep DB config
# Right now we're using SQLite (local file-based DB)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "timetable.db")

# If in future you want to swap DB engines, you can just update this variable
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
