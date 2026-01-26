from flask import Flask, render_template, request, redirect, session
import os

from config import SECRET_KEY, UPLOAD_FOLDER
from models import init_db, save_candidate, get_all_candidates
from ai_engine import ai_score_candidate
from admin import admin_login_check

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

init_db()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/apply", methods=["GET","POST"])
def apply():
    if request.method == "POST":
        resume = request.files["resume"]
        resume_path = os.path.join(app.config["UPLOAD_FOLDER"], resume.filename)
        resume.save(resume_path)

        score, result = ai_score_candidate(
            request.form["experience"],
            request.form["qualification"]
        )

        data = {
            "Name": request.form["name"],
            "Phone": request.form["phone"],
            "Email": request.form["email"],
            "Experience": request.form["experience"],
            "Qualification": request.form["qualification"],
            "Job Role": request.form["job_role"],
            "Country": request.form["country"],
            "State": request.form["state"],
            "District": request.form["district"],
            "Area": request.form["area"],
            "AI Score": score,
            "Result": result,
            "Resume": resume.filename
        }

        save_candidate(data)
        return "Application Submitted Successfully"

    return render_template("apply.html")

@app.route("/admin", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        if admin_login_check(
            request.form["username"],
            request.form["password"]
        ):
            session["admin"] = True
            return redirect("/dashboard")
    return render_template("admin_login.html")

@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/admin")
    candidates = get_all_candidates()
    return render_template("admin_dashboard.html", data=candidates)

if __name__ == "__main__":
    app.run()
