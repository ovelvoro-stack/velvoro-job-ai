from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
app.secret_key = "velvoro_secret_key"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ------------------------
# In-memory DB (replace later)
# ------------------------
CANDIDATES = []
PAID_JOBS = ["Software Engineer", "Data Analyst"]

# ------------------------
# AI SCORING LOGIC
# ------------------------
def ai_score(candidate):
    score = 0

    if candidate["experience"] != "Fresher":
        score += 30
    if candidate["qualification"] in ["Degree", "B.Tech", "M.Tech", "MBA"]:
        score += 30
    if candidate["job_role"] in PAID_JOBS:
        score += 40

    result = "PASS" if score >= 60 else "FAIL"
    return score, result

# ------------------------
# ROUTES
# ------------------------

@app.route("/")
def index():
    return render_template("index.html")

# ------------------------
# APPLY JOB
# ------------------------
@app.route("/apply", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        resume = request.files["resume"]
        filename = secure_filename(resume.filename)
        resume.save(os.path.join(UPLOAD_FOLDER, filename))

        candidate = {
            "id": str(uuid.uuid4()),
            "name": request.form["name"],
            "phone": request.form["phone"],
            "email": request.form["email"],
            "experience": request.form["experience"],
            "qualification": request.form["qualification"],
            "job_role": request.form["job_role"],
            "country": request.form["country"],
            "state": request.form["state"],
            "district": request.form["district"],
            "area": request.form["area"],
            "resume": filename
        }

        score, result = ai_score(candidate)
        candidate["ai_score"] = score
        candidate["result"] = result

        CANDIDATES.append(candidate)

        return redirect(url_for("index"))

    return render_template("apply.html")

# ------------------------
# ADMIN LOGIN
# ------------------------
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            session["admin"] = True
            return redirect(url_for("dashboard"))
    return render_template("admin_login.html")

# ------------------------
# DASHBOARD
# ------------------------
@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    search = request.args.get("search", "").lower()

    filtered = [
        c for c in CANDIDATES
        if search in c["name"].lower()
        or search in c["job_role"].lower()
        or search in c["result"].lower()
    ]

    return render_template("dashboard.html", candidates=filtered)

# ------------------------
# LOGOUT
# ------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
