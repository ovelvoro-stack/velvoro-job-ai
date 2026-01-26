import os
import csv
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ---------- CONFIG ----------
UPLOAD_FOLDER = "uploads"
DATA_FOLDER = "data"
CSV_FILE = os.path.join(DATA_FOLDER, "applications.csv")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

# ---------- INIT CSV ----------
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Name", "Phone", "Email",
            "Category", "Experience",
            "Company", "Resume"
        ])

# ---------- ROUTES ----------
@app.route("/")
def apply():
    return render_template("apply.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    phone = request.form["phone"]
    email = request.form["email"]
    category = request.form["category"]
    experience = request.form["experience"]
    company = request.form["company"]

    resume = request.files["resume"]
    filename = secure_filename(resume.filename)
    resume.save(os.path.join(UPLOAD_FOLDER, filename))

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            name, phone, email,
            category, experience,
            company, filename
        ])

    return redirect(url_for("success"))

@app.route("/success")
def success():
    return render_template("success.html")

# ---------- ADMIN ----------
@app.route("/admin")
def admin():
    data = []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            data.append(row)
    return render_template("admin.html", data=data)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
