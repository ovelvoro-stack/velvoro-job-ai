import os
import csv
from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "velvoro_secret")

UPLOAD_FOLDER = "uploads"
DB_FILE = "velvoro_jobs.csv"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

FIELDS = [
    "Name",
    "Phone",
    "Email",
    "Category",
    "Country",
    "State",
    "District",
    "Resume"
]

# ---------- INIT CSV ----------
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(FIELDS)

# ---------- HOME / JOB APPLY ----------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = {}
        for field in FIELDS[:-1]:
            data[field] = request.form.get(field, "")

        resume = request.files.get("Resume")
        filename = ""
        if resume:
            filename = secure_filename(resume.filename)
            resume.save(os.path.join(UPLOAD_FOLDER, filename))

        data["Resume"] = filename

        with open(DB_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(data.values())

        return redirect(url_for("success"))

    return render_template("index.html")

# ---------- SUCCESS ----------
@app.route("/success")
def success():
    return render_template("success.html")

# ---------- ADMIN ----------
@app.route("/admin")
def admin():
    rows = []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        for row in reader:
            rows.append(row)
    return render_template("admin.html", headers=headers, rows=rows)

# ---------- DOWNLOAD EXCEL ----------
@app.route("/download")
def download():
    return send_file(DB_FILE, as_attachment=True)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
