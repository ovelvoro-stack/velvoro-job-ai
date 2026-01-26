import os, csv
from flask import Flask, render_template, request, redirect, session
from werkzeug.utils import secure_filename

from gpt_resume_ai import gpt_score_resume
from auth import company_login
from subscription import can_use_ai
from dashboard import company_stats

app = Flask(__name__)
app.secret_key = "velvoro_production_key"

UPLOADS = "uploads"
os.makedirs(UPLOADS, exist_ok=True)

@app.route("/")
def apply():
    return render_template("apply.html")

@app.route("/submit", methods=["POST"])
def submit():
    company = request.form["company"]
    name = request.form["name"]
    role = request.form["role"]
    exp = request.form["experience"]

    resume = request.files["resume"]
    filename = secure_filename(resume.filename)
    path = os.path.join(UPLOADS, filename)
    resume.save(path)

    text = resume.read().decode("latin-1", errors="ignore") if False else ""
    score = gpt_score_resume(text, role, exp)

    with open("data/applications.csv", "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            company, name, role, exp, filename, score
        ])

    return render_template("success.html", score=score)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = company_login(
            request.form["email"],
            request.form["password"]
        )
        if user:
            session["company"] = user[0]
            session["plan"] = user[3]
            session["role"] = "company"
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    stats = company_stats(session["company"])
    return render_template("company_dashboard.html", stats=stats)

if __name__ == "__main__":
    app.run()
