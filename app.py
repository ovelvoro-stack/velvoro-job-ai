import os, csv
from flask import Flask, render_template, request, redirect, session
from werkzeug.utils import secure_filename

from questions import QUESTIONS
from ai_engine import score_resume
from auth import auth
from admin import admin

app = Flask(__name__)
app.secret_key = "velvoro_secret"

app.register_blueprint(auth)
app.register_blueprint(admin)

os.makedirs("uploads", exist_ok=True)
os.makedirs("data", exist_ok=True)

DB = "data/applications.csv"

if not os.path.exists(DB):
    with open(DB,"w",newline="",encoding="utf-8") as f:
        csv.writer(f).writerow([
            "Name","Email","JobType","Score","QuizScore","ResumeScore","Paid"
        ])

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        session["form"] = dict(request.form)
        session["job"] = request.form["JobType"]
        return redirect("/questions")
    return render_template("index.html")

@app.route("/questions", methods=["GET","POST"])
def questions():
    job = session["job"]
    qs = QUESTIONS[job]

    if request.method == "POST":
        correct = 0
        for i,q in enumerate(qs):
            if request.form.get(f"q{i}") == q["answer"]:
                correct += 1

        resume_score = score_resume(session["form"].get("resume_text",""))
        total = correct * 10

        with open(DB,"a",newline="",encoding="utf-8") as f:
            csv.writer(f).writerow([
                session["form"]["Name"],
                session["form"]["Email"],
                job,
                total + resume_score,
                correct,
                resume_score,
                "YES" if session["form"].get("Paid") else "NO"
            ])

        return redirect("/success")

    return render_template("questions.html", questions=qs)

@app.route("/success")
def success():
    return render_template("success.html")

if __name__ == "__main__":
    app.run()
