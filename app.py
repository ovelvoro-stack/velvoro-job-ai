from flask import Flask, render_template, request, redirect, url_for
import csv, os

app = Flask(__name__)

DATA_FILE = "data/applications.csv"

def save_candidate(data):
    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/apply", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        data = {
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
            "ai_score": "Pending",
            "result": "Pending"
        }
        save_candidate(data)
        return "<h2>✅ Application Submitted Successfully</h2><a href='/'>Back to Home</a>"
    return render_template("apply.html")

@app.route("/admin")
def admin():
    return render_template("admin_login.html")

@app.route("/dashboard")
def dashboard():
    applications = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            applications = list(reader)
    return render_template("dashboard.html", applications=applications)

if __name__ == "__main__":
    app.run(debug=True)
