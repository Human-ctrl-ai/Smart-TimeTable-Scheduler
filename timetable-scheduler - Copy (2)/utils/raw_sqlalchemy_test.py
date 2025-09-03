# raw_sqlalchemy_test.py
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base

# 1️⃣ Set up SQLite engine
engine = create_engine("sqlite:///timetable.db", echo=True)

# 2️⃣ Declare a base model
Base = declarative_base()

# 3️⃣ Define a test table
class Classroom(Base):
    __tablename__ = "classroom"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)

# 4️⃣ Actually create the table
Base.metadata.create_all(engine)
print("✅ Table created with pure SQLAlchemy!")
