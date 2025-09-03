from db_extensions import db   # keep consistent import


class Classroom(db.Model):
    __tablename__ = "classroom"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Classroom {self.name} (Capacity: {self.capacity})>"


class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    max_classes_per_day = db.Column(db.Integer, nullable=False, default=6)

    # ✅ Add this field
    avg_leaves_per_month = db.Column(db.Integer, nullable=False, default=0)

    subjects = db.relationship("Subject", backref="faculty", lazy=True)

    def __repr__(self):
        return f"<Faculty {self.name}>"


class Subject(db.Model):
    __tablename__ = "subject"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    course_code = db.Column(db.String(20), nullable=False, unique=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)
    classes_per_week = db.Column(db.Integer, nullable=False, default=1)
    
    def __repr__(self):
        return f"<Subject {self.name} ({self.course_code})>"


class Batch(db.Model):
    __tablename__ = "batch"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    num_students = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Batch {self.name}>"
    

class SpecialClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey("batch.id"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("classroom.id"), nullable=False)

    day = db.Column(db.String(20), nullable=False)   # e.g. "Monday"
    period = db.Column(db.Integer, nullable=False)   # e.g. 1–12

    # Relationships (for easier joins)
    subject = db.relationship("Subject", backref="special_classes")
    batch = db.relationship("Batch", backref="special_classes")
    classroom = db.relationship("Classroom", backref="special_classes")

    def __repr__(self):
        return f"<SpecialClass {self.subject.name} - {self.batch.name} on {self.day} (Period {self.period})>"


class Timetable(db.Model):
    __tablename__ = "timetable"

    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey("classroom.id"))
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"))
    batch_id = db.Column(db.Integer, db.ForeignKey("batch.id"))
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"))
    day = db.Column(db.String(20))   # e.g., Monday
    period = db.Column(db.Integer)   # e.g., 1,2,3,4...

    classroom = db.relationship("Classroom", backref="timetables")
    subject = db.relationship("Subject", backref="timetables")
    batch = db.relationship("Batch", backref="timetables")
    faculty = db.relationship("Faculty", backref="timetables")

    def __repr__(self):
        return f"<Timetable {self.day} Period {self.period}>"
