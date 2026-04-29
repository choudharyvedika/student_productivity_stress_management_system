from flask import Blueprint, request, render_template, redirect, session
from models.db import get_connection
import hashlib

auth_bp = Blueprint("auth", __name__)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route("/")
def login_page():
    return render_template("login.html")

@auth_bp.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = hash_password(request.form["password"])

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM USER_AUTH WHERE email=%s AND password=%s", (email, password))
    user = cursor.fetchone()

    if user:
        session["user_id"] = user["user_id"]  # keep this
        session["student_id"] = user["student_id"]  # this is the important one
        return redirect("/dashboard")

    return "Invalid login"
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    email = request.form["email"]
    password = hash_password(request.form["password"])

    conn = get_connection()
    cursor = conn.cursor()

    # Create student
    cursor.execute("""
        INSERT INTO STUDENT (first_name, last_name, email, enrollment_date)
        VALUES (%s, %s, %s, CURDATE())
    """, ("Student", "User", email))

    student_id = cursor.lastrowid

    # Create auth user linked to student
    cursor.execute("""
        INSERT INTO USER_AUTH (email, password, student_id)
        VALUES (%s, %s, %s)
    """, (email, password, student_id))

    conn.commit()

    return redirect("/")