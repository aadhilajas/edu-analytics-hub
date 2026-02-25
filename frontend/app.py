import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import jwt
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-flask-key")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

# --- Decorators ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] not in roles:
                flash("You don't have permission to access this page.", "danger")
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_headers():
    return {"Authorization": f"Bearer {session.get('token')}"}

# --- Common Routes ---

@app.route("/", methods=["GET", "POST"])
def login():
    if 'token' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        data = {"username": email, "password": password}
        response = requests.post(f"{API_BASE_URL}/auth/login", data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            session['token'] = token_data['access_token']
            
            # Decode JWT to get role
            decoded = jwt.decode(session['token'], options={"verify_signature": False})
            session['role'] = decoded.get('role', 'student') 
            session['email'] = decoded.get('sub', '')
            
            return redirect(url_for('dashboard'))
        else:
            flash(f"Invalid email or password. API Response {response.status_code}: {response.text}", "danger")
            
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route("/dashboard")
@login_required
def dashboard():
    role = session.get('role')
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    elif role == 'student':
        return redirect(url_for('student_dashboard'))
    return redirect(url_for('logout'))

def fetch_api(url, fallback=None):
    try:
        response = requests.get(url, headers=get_headers())
        if response.status_code == 401:
            session.clear()
            flash("Your session has expired. Please log in again.", "warning")
            return None, True # True means redirect to login
        if response.status_code != 200:
            flash(f"API Error ({response.status_code}): {response.text}", "danger")
            return fallback, False
        return response.json(), False
    except requests.exceptions.ConnectionError:
        flash("Could not connect to the backend API. Is FastAPI running?", "danger")
        return fallback, False

# ==========================================
# ADMIN ROUTES
# ==========================================

@app.route("/admin/dashboard")
@login_required
@role_required(["admin"])
def admin_dashboard():
    return render_template("admin/dashboard.html", role="admin")

@app.route("/admin/students", methods=["GET", "POST"])
@login_required
@role_required(["admin"])
def admin_students():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            data = {
                "name": request.form.get("name"),
                "email": request.form.get("email"),
                "password": request.form.get("password"),
                "class_name": request.form.get("class_name"),
                "roll_number": request.form.get("roll_number")
            }
            res = requests.post(f"{API_BASE_URL}/admin/students/", json=data, headers=get_headers())
            if res.status_code == 200:
                flash("Student added successfully!", "success")
            else:
                flash(f"Error adding student: {res.text}", "danger")
        elif action == "delete":
            student_id = request.form.get("student_id")
            res = requests.delete(f"{API_BASE_URL}/admin/students/{student_id}", headers=get_headers())
            if res.status_code == 200:
                flash("Student deleted successfully!", "success")
            else:
                flash(f"Error deleting student: {res.text}", "danger")
        return redirect(url_for('admin_students'))

    students, redir = fetch_api(f"{API_BASE_URL}/admin/students/", fallback=[])
    if redir: return redirect(url_for('login'))
    return render_template("admin/students.html", students=students, role="admin")

@app.route("/admin/teachers", methods=["GET", "POST"])
@login_required
@role_required(["admin"])
def admin_teachers():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            data = {
                "name": request.form.get("name"),
                "email": request.form.get("email"),
                "password": request.form.get("password")
            }
            res = requests.post(f"{API_BASE_URL}/admin/teachers/", json=data, headers=get_headers())
            if res.status_code == 200:
                flash("Teacher added successfully!", "success")
            else:
                flash(f"Error adding teacher: {res.text}", "danger")
        elif action == "delete":
            teacher_id = request.form.get("teacher_id")
            res = requests.delete(f"{API_BASE_URL}/admin/teachers/{teacher_id}", headers=get_headers())
            if res.status_code == 200:
                flash("Teacher deleted successfully!", "success")
            else:
                flash(f"Error deleting teacher: {res.text}", "danger")
        return redirect(url_for('admin_teachers'))

    teachers, redir = fetch_api(f"{API_BASE_URL}/admin/teachers/", fallback=[])
    if redir: return redirect(url_for('login'))
    return render_template("admin/teachers.html", teachers=teachers, role="admin")

@app.route("/admin/subjects", methods=["GET", "POST"])
@login_required
@role_required(["admin"])
def admin_subjects():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            data = {"name": request.form.get("name")}
            res = requests.post(f"{API_BASE_URL}/admin/subjects/", json=data, headers=get_headers())
            if res.status_code == 200:
                flash("Subject added successfully!", "success")
            else:
                flash(f"Error adding subject: {res.text}", "danger")
        elif action == "delete":
            subject_id = request.form.get("subject_id")
            res = requests.delete(f"{API_BASE_URL}/admin/subjects/{subject_id}", headers=get_headers())
            if res.status_code == 200:
                flash("Subject deleted successfully!", "success")
            else:
                flash(f"Error deleting subject: {res.text}", "danger")
        elif action == "assign":
            subject_id = request.form.get("subject_id")
            teacher_id = request.form.get("teacher_id")
            if teacher_id:
                data = {"teacher_id": int(teacher_id)}
                res = requests.put(f"{API_BASE_URL}/admin/subjects/{subject_id}/assign", json=data, headers=get_headers())
                if res.status_code == 200:
                    flash("Teacher assigned successfully!", "success")
                else:
                    flash(f"Error assigning teacher: {res.text}", "danger")
        return redirect(url_for('admin_subjects'))

    subjects, redir = fetch_api(f"{API_BASE_URL}/admin/subjects/", fallback=[])
    if redir: return redirect(url_for('login'))
    teachers, redir2 = fetch_api(f"{API_BASE_URL}/admin/teachers/", fallback=[])
    if redir2: return redirect(url_for('login'))
    return render_template("admin/subjects.html", subjects=subjects, teachers=teachers, role="admin")

@app.route("/admin/analytics")
@login_required
@role_required(["admin"])
def admin_analytics():
    leaderboard, redir = fetch_api(f"{API_BASE_URL}/analytics/admin/leaderboard", fallback=[])
    if redir: return redirect(url_for('login'))
    subjects, redir2 = fetch_api(f"{API_BASE_URL}/analytics/admin/subjects", fallback=[])
    if redir2: return redirect(url_for('login'))
    return render_template("admin/analytics.html", leaderboard=leaderboard, subjects=subjects, role="admin")

# ==========================================
# TEACHER ROUTES
# ==========================================

@app.route("/teacher/dashboard")
@login_required
@role_required(["teacher"])
def teacher_dashboard():
    return render_template("teacher/dashboard.html", role="teacher")

@app.route("/teacher/subjects")
@login_required
@role_required(["teacher"])
def teacher_subjects():
    subjects, redir = fetch_api(f"{API_BASE_URL}/teacher/subjects/", fallback=[])
    if redir: return redirect(url_for('login'))
    return render_template("teacher/subjects.html", subjects=subjects, role="teacher")

@app.route("/teacher/students")
@login_required
@role_required(["teacher"])
def teacher_students():
    students, redir = fetch_api(f"{API_BASE_URL}/teacher/students/", fallback=[])
    if redir: return redirect(url_for('login'))
    return render_template("teacher/students.html", students=students, role="teacher")

@app.route("/teacher/add_marks")
@login_required
@role_required(["teacher"])
def teacher_add_marks():
    subjects, redir = fetch_api(f"{API_BASE_URL}/teacher/subjects/", fallback=[])
    if redir: return redirect(url_for('login'))
    students, redir2 = fetch_api(f"{API_BASE_URL}/teacher/students/", fallback=[])
    if redir2: return redirect(url_for('login'))
    return render_template("teacher/add_marks.html", subjects=subjects, students=students, role="teacher")

@app.route("/teacher/analytics")
@login_required
@role_required(["teacher"])
def teacher_analytics():
    subjects, redir = fetch_api(f"{API_BASE_URL}/analytics/teacher/subjects", fallback=[])
    if redir: return redirect(url_for('login'))
    return render_template("teacher/analytics.html", subjects=subjects, role="teacher")

# ==========================================
# STUDENT ROUTES
# ==========================================

@app.route("/student/dashboard")
@login_required
@role_required(["student"])
def student_dashboard():
    return render_template("student/dashboard.html", role="student")

@app.route("/student/marks")
@login_required
@role_required(["student"])
def student_marks():
    marks, redir = fetch_api(f"{API_BASE_URL}/student/marks", fallback=[])
    if redir: return redirect(url_for('login'))
    return render_template("student/marks.html", marks=marks, role="student")

@app.route("/student/analytics")
@login_required
@role_required(["student"])
def student_analytics():
    stats, redir = fetch_api(f"{API_BASE_URL}/analytics/student/stats", fallback={})
    if redir: return redirect(url_for('login'))
    return render_template("student/analytics.html", stats=stats, role="student")

@app.route("/student/profile")
@login_required
@role_required(["student"])
def student_profile():
    profile, redir = fetch_api(f"{API_BASE_URL}/student/profile", fallback=None)
    if redir: return redirect(url_for('login'))
    
    if profile is None:
        return redirect(url_for('student_dashboard'))
        
    return render_template("student/profile.html", profile=profile, role="student")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
