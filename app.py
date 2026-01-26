from flask import Flask, render_template, request, redirect, session
from models import init_db
from database import get_db
from auth import hash_password, verify_password
from config import SECRET_KEY
import os

app = Flask(__name__)
app.secret_key = SECRET_KEY

init_db()

# HOME
@app.route("/")
def home():
    return render_template("home.html")

# JOB LIST
@app.route("/jobs")
def jobs():
    db = get_db()
    jobs = db.execute("SELECT * FROM jobs").fetchall()
    return render_template("jobs.html", jobs=jobs)

# APPLY JOB
@app.route("/apply/<int:job_id>", methods=["GET","POST"])
def apply(job_id):
    if request.method == "POST":
        name = request.form["name"]
        resume = request.files["resume"]
        resume_path = f"static/resumes/{resume.filename}"
        resume.save(resume_path)

        db = get_db()
        db.execute("""
        INSERT INTO users (name,resume,country)
        VALUES (?,?,?)
        """,(name,resume_path,"India"))
        db.commit()

        return "Applied Successfully"
    return render_template("apply.html")

# REGISTER
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        db = get_db()
        db.execute("""
        INSERT INTO users (name,email,password)
        VALUES (?,?,?)
        """,(request.form["name"],
             request.form["email"],
             hash_password(request.form["password"])))
        db.commit()
        return redirect("/login")
    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email=?",
            (request.form["email"],)
        ).fetchone()

        if user and verify_password(user[4], request.form["password"]):
            session["user"] = user[0]
            return redirect("/profile")
    return render_template("login.html")

# PROFILE
@app.route("/profile")
def profile():
    return "User Profile"

# ADMIN LOGIN
@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method=="POST":
        if request.form["user"]=="admin" and request.form["pass"]=="admin":
            session["admin"]=True
            return redirect("/admin/dashboard")
    return render_template("admin_login.html")

# ADMIN DASHBOARD
@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin/login")
    db = get_db()
    count = db.execute("SELECT COUNT(*) FROM applications").fetchone()
    return render_template("admin_dashboard.html", count=count)

if __name__ == "__main__":
    app.run(debug=True)
