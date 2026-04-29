from flask import Blueprint, render_template, request, redirect, session
from models.db import get_connection

activity_bp = Blueprint("activity", __name__)
def calculate_metrics(study, sleep, screen, exercise, social):
    stress = 5
    productivity = 5

    # Stress rules
    if sleep < 6:
        stress += 2
    if screen > 5:
        stress += 1
    if social > 4:
        stress += 1

    # Productivity rules
    if study > 4:
        productivity += 2
    if exercise > 20:
        productivity += 1
    if sleep >= 7:
        productivity += 1

    # Clamp between 1–10
    stress = max(1, min(10, stress))
    productivity = max(1, min(10, productivity))

    return stress, productivity


# DASHBOARD
@activity_bp.route("/dashboard")
def dashboard():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT a.*, p.stress_score, p.productivity_score
        FROM ACTIVITY_LOG a
        LEFT JOIN PREDICTED_METRICS p ON a.activity_id = p.activity_id
        WHERE a.student_id = %s
        ORDER BY a.activity_date DESC
    """, (session["student_id"],))

    activities = cursor.fetchall()

    return render_template("dashboard.html", activities=activities)


# ADD ACTIVITY
@activity_bp.route("/add-activity", methods=["GET", "POST"])
def add_activity():
    if "student_id" not in session:
        return redirect("/")

    if request.method == "GET":
        return render_template("add_activity.html")

    print("FORM RECEIVED")   # 👈 add this

    conn = get_connection()
    cursor = conn.cursor()

    data = (
        session["student_id"],
        request.form["date"],
        request.form["study"],
        request.form["sleep"],
        request.form["screen"],
        request.form["exercise"],
        request.form["social"]
    )

    print("DATA:", data)   # 👈 add this

    cursor.execute("""
        INSERT INTO ACTIVITY_LOG 
        (student_id, activity_date, study_hours, sleep_hours, screen_time, exercise_minutes, social_hours)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, data)

    # 🔥 IMPORTANT: get activity_id BEFORE commit
    activity_id = cursor.lastrowid

    # Extract form values
    study = int(request.form["study"])
    sleep = int(request.form["sleep"])
    screen = int(request.form["screen"])
    exercise = int(request.form["exercise"])
    social = int(request.form["social"])

    # Calculate prediction
    stress, productivity = calculate_metrics(study, sleep, screen, exercise, social)

    # Insert into PREDICTED_METRICS
    cursor.execute("""
        INSERT INTO PREDICTED_METRICS 
        (activity_id, stress_score, productivity_score, prediction_timestamp)
        VALUES (%s, %s, %s, NOW())
    """, (activity_id, stress, productivity))

    # ✅ commit AFTER both inserts
    conn.commit()

    print("INSERT + PREDICTION DONE")

    return redirect("/dashboard")

@activity_bp.route("/view-activity")
def view_activity():
    if "student_id" not in session:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM ACTIVITY_LOG
        WHERE student_id = %s
        ORDER BY activity_date DESC
    """, (session["student_id"],))

    activities = cursor.fetchall()

    return render_template("view_activity.html", activities=activities)

@activity_bp.route("/activity/<int:activity_id>")
def activity_detail(activity_id):
    if "student_id" not in session:
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM ACTIVITY_LOG
        WHERE activity_id = %s AND student_id = %s
    """, (activity_id, session["student_id"]))

    activity = cursor.fetchone()

    return render_template("activity_detail.html", activity=activity)