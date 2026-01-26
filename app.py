import os, csv
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

from auth import check_login
from resume_ai import score_resume
from subscription import can_post_job

app = Flask(__name__)
app.secret_key = "velvoro_secret"

UPLOAD_FOLDER = "uploads"
DATA_FOLDER = "data"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

APP_FILE = f"{DATA_FOLDER}/applications.csv"

@app.route("/")
def apply():
    return render_template("apply.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    category = request.form["category"]
    experience = request.form["experience"]

    resume = request.files["resume"]
    filename = secure_filename(resume.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    resume.save(path)

    text = resume.read().decode("latin-1", errors="ignore") if False else ""
    score = score_resume(text, category, experience)

    with open(APP_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([name, category, experience, score, filename])

    return render_template("success.html", score=score)

# ---------- ADMIN ----------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if check_login(request.form["username"], request.form["password"]):
            session["admin"] = True
            return redirect("/admin")
    return render_template("login.html")

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    data = []
    with open(APP_FILE, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            data.append(row)
    return render_template("admin.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
