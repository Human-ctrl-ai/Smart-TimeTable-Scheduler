from flask import Flask, send_file, request, render_template, redirect, url_for
from config import SECRET_KEY, SQLALCHEMY_DATABASE_URI
from db_extensions import db
import os
from genetic_scheduler import GeneticScheduler, DAYS

# --- Initialize App ---
app = Flask(__name__)
app.secret_key = SECRET_KEY

# --- DB Setup ---
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# --- Import Models AFTER db init ---
from models import Classroom, Faculty, Subject, Batch, Timetable, SpecialClass

# ---------------- ROOT ROUTE ----------------
@app.route("/")
def home():
    return render_template("base.html")

# ---------------- HEALTH CHECK ----------------
@app.route("/health/db")
def health_db():
    from sqlalchemy import text
    try:
        db.session.execute(text("SELECT 1"))
        return "DB connection OK ✅"
    except Exception as e:
        return f"DB Error ❌: {e}"

# ---------------- CLASSROOM ROUTES ----------------
@app.route("/classrooms")
def list_classrooms():
    classrooms = Classroom.query.all()
    return render_template("classrooms.html", classrooms=classrooms)

@app.route("/classrooms/add", methods=["GET", "POST"])
def add_classroom():
    if request.method == "POST":
        classroom = Classroom(
            name=request.form["name"],
            capacity=int(request.form["capacity"])
        )
        db.session.add(classroom)
        db.session.commit()
        return redirect(url_for("list_classrooms"))
    return render_template("add_classroom.html")

@app.route("/classrooms/edit/<int:id>", methods=["GET", "POST"])
def edit_classroom(id):
    classroom = Classroom.query.get_or_404(id)
    if request.method == "POST":
        classroom.name = request.form["name"]
        classroom.capacity = int(request.form["capacity"])
        db.session.commit()
        return redirect(url_for("list_classrooms"))
    return render_template("edit_classroom.html", classroom=classroom)

@app.route("/classrooms/delete/<int:id>")
def delete_classroom(id):
    classroom = Classroom.query.get_or_404(id)
    db.session.delete(classroom)
    db.session.commit()
    return redirect(url_for("list_classrooms"))

# ---------------- FACULTY ROUTES ----------------
@app.route("/faculties")
def list_faculties():
    faculties = Faculty.query.all()
    return render_template("faculties.html", faculties=faculties)

@app.route("/faculties/add", methods=["GET", "POST"])
def add_faculty():
    if request.method == "POST":
        faculty = Faculty(
            name=request.form["name"],
            max_classes_per_day=int(request.form["max_classes_per_day"]),
            avg_leaves_per_month=int(request.form["avg_leaves_per_month"])
        )
        db.session.add(faculty)
        db.session.commit()
        return redirect(url_for("list_faculties"))
    return render_template("add_faculty.html")

@app.route("/faculties/edit/<int:id>", methods=["GET", "POST"])
def edit_faculty(id):
    faculty = Faculty.query.get_or_404(id)
    if request.method == "POST":
        faculty.name = request.form["name"]
        faculty.max_classes_per_day = int(request.form["max_classes_per_day"])
        faculty.avg_leaves_per_month = int(request.form["avg_leaves_per_month"])
        db.session.commit()
        return redirect(url_for("list_faculties"))
    return render_template("edit_faculty.html", faculty=faculty)

@app.route("/faculties/delete/<int:id>")
def delete_faculty(id):
    faculty = Faculty.query.get_or_404(id)
    db.session.delete(faculty)
    db.session.commit()
    return redirect(url_for("list_faculties"))

# ---------------- SUBJECT ROUTES ----------------
@app.route("/subjects")
def list_subjects():
    subjects = Subject.query.all()
    faculties = Faculty.query.all()
    return render_template("subjects.html", subjects=subjects, faculties=faculties)

@app.route("/subjects/add", methods=["GET", "POST"])
def add_subject():
    faculties = Faculty.query.all()
    if request.method == "POST":
        subject = Subject(
            name=request.form["name"],
            course_code=request.form["course_code"],
            faculty_id=int(request.form["faculty_id"]),
            classes_per_week=int(request.form["classes_per_week"])
        )
        db.session.add(subject)
        db.session.commit()
        return redirect(url_for("list_subjects"))
    return render_template("add_subject.html", faculties=faculties)

@app.route("/subjects/edit/<int:id>", methods=["GET", "POST"])
def edit_subject(id):
    subject = Subject.query.get_or_404(id)
    faculties = Faculty.query.all()
    if request.method == "POST":
        subject.name = request.form["name"]
        subject.course_code = request.form["course_code"]
        subject.faculty_id = int(request.form["faculty_id"])
        subject.classes_per_week = int(request.form["classes_per_week"])
        db.session.commit()
        return redirect(url_for("list_subjects"))
    return render_template("edit_subject.html", subject=subject, faculties=faculties)

@app.route("/subjects/delete/<int:id>")
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for("list_subjects"))

# ---------------- BATCH ROUTES ----------------
@app.route("/batches")
def list_batches():
    batches = Batch.query.all()
    return render_template("batches.html", batches=batches)

@app.route("/batches/add", methods=["GET", "POST"])
def add_batch():
    if request.method == "POST":
        batch = Batch(
            name=request.form["name"],
            num_students=int(request.form["num_students"])
        )
        db.session.add(batch)
        db.session.commit()
        return redirect(url_for("list_batches"))
    return render_template("add_batch.html")

@app.route("/batches/edit/<int:id>", methods=["GET", "POST"])
def edit_batch(id):
    batch = Batch.query.get_or_404(id)
    if request.method == "POST":
        batch.name = request.form["name"]
        batch.num_students = int(request.form["num_students"])
        db.session.commit()
        return redirect(url_for("list_batches"))
    return render_template("edit_batch.html", batch=batch)

@app.route("/batches/delete/<int:id>")
def delete_batch(id):
    batch = Batch.query.get_or_404(id)
    db.session.delete(batch)
    db.session.commit()
    return redirect(url_for("list_batches"))

# ---------------- SPECIAL CLASS ROUTES ----------------
@app.route("/special_classes")
def list_special_classes():
    special_classes = SpecialClass.query.all()
    return render_template("special_classes.html", special_classes=special_classes)

@app.route("/special_classes/add", methods=["GET", "POST"])
def add_special_class():
    subjects = Subject.query.all()
    batches = Batch.query.all()
    classrooms = Classroom.query.all()
    if request.method == "POST":
        sc = SpecialClass(
            subject_id=int(request.form["subject_id"]),
            batch_id=int(request.form["batch_id"]),
            room_id=int(request.form["room_id"]),
            day=request.form["day"],
            period=int(request.form["period"])
        )
        db.session.add(sc)
        db.session.commit()
        return redirect(url_for("list_special_classes"))
    return render_template("add_special_class.html",
                           subjects=subjects, batches=batches, classrooms=classrooms)

@app.route("/special_classes/edit/<int:id>", methods=["GET", "POST"])
def edit_special_class(id):
    sc = SpecialClass.query.get_or_404(id)
    subjects = Subject.query.all()
    batches = Batch.query.all()
    classrooms = Classroom.query.all()
    if request.method == "POST":
        sc.subject_id = int(request.form["subject_id"])
        sc.batch_id = int(request.form["batch_id"])
        sc.room_id = int(request.form["room_id"])
        sc.day = request.form["day"]
        sc.period = int(request.form["period"])
        db.session.commit()
        return redirect(url_for("list_special_classes"))
    return render_template("edit_special_class.html",
                           sc=sc, subjects=subjects, batches=batches, classrooms=classrooms)

@app.route("/special_classes/delete/<int:id>")
def delete_special_class(id):
    sc = SpecialClass.query.get_or_404(id)
    db.session.delete(sc)
    db.session.commit()
    return redirect(url_for("list_special_classes"))

# ---------------- TIMETABLE GENERATION ----------------
@app.route("/generate_timetable")
def generate_timetable():
    subjects = Subject.query.all()
    faculties = Faculty.query.all()
    batches = Batch.query.all()
    classrooms = Classroom.query.all()

    if not subjects or not faculties or not batches or not classrooms:
        return "❌ Missing data in DB. Please add data first."

    scheduler = GeneticScheduler(
        subjects=subjects,
        faculties=faculties,
        batches=batches,
        classrooms=classrooms,
        days=DAYS,
        periods_per_day=6,
        population_size=10
    )

    best_timetable = scheduler.run(generations=50)
    html = scheduler.pretty_table(best_timetable)
    scheduler.print_population_report(best_only=True)

    return html

@app.route("/download_timetable")
def download_timetable():
    path = os.path.join(os.path.dirname(__file__), "timetable.html")
    if not os.path.exists(path):
        return "❌ Timetable not generated yet."
    return send_file(path, as_attachment=True)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
