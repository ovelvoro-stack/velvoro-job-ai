from flask import Flask, request, redirect, url_for, render_template_string
import csv, os
from datetime import datetime

# ---------------- CONFIG ----------------
app = Flask(__name__)
DATA_FILE = "applications.csv"

# Create CSV if not exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "name", "phone", "email", "job_role",
            "country", "state", "district", "area",
            "resume_filename", "ai_score", "applied_at"
        ])

# ---------------- AI SCORING (SIMPLE & SAFE) ----------------
def calculate_ai_score(resume_text):
    # Simple stable logic (Render safe)
    if not resume_text:
        return 0
    keywords = ["python", "java", "sql", "api", "react", "cloud"]
    score = sum(1 for k in keywords if k in resume_text.lower())
    return min(score * 15, 100)

# ---------------- HOME ----------------
@app.route("/")
def home():
    return redirect("/apply")

# ---------------- APPLY ----------------
@app.route("/apply", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        job_role = request.form["job_role"]
        country = request.form["country"]
        state = request.form["state"]
        district = request.form["district"]
        area = request.form["area"]

        resume = request.files["resume"]
        resume_text = resume.read().decode("utf-8", errors="ignore")
        ai_score = calculate_ai_score(resume_text)

        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                name, phone, email, job_role,
                country, state, district, area,
                resume.filename, ai_score,
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ])

        return "<h3 class='text-center mt-5'>Application Submitted Successfully</h3>"

    return render_template_string(APPLY_HTML)

# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    applications = []
    with open(DATA_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        applications = list(reader)

    total = len(applications)
    avg_score = round(
        sum(int(a["ai_score"]) for a in applications) / total, 2
    ) if total else 0

    return render_template_string(
        ADMIN_HTML,
        applications=applications,
        total=total,
        avg_score=avg_score
    )

# ---------------- UI TEMPLATES ----------------
APPLY_HTML = """
<!doctype html>
<html>
<head>
<title>Velvoro Job Application</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5">
<div class="card shadow p-4">
<h3 class="mb-4 text-center">Velvoro Software Solution – Job Apply</h3>

<form method="post" enctype="multipart/form-data">
<div class="row">
<div class="col-md-6 mb-3">
<label>Full Name</label>
<input name="name" class="form-control" required>
</div>

<div class="col-md-6 mb-3">
<label>Phone Number</label>
<input name="phone" class="form-control" required>
</div>

<div class="col-md-6 mb-3">
<label>Email</label>
<input name="email" type="email" class="form-control" required>
</div>

<div class="col-md-6 mb-3">
<label>Job Role</label>
<select name="job_role" class="form-select" required>
<optgroup label="IT Jobs">
<option>Software Engineer</option>
<option>Backend Developer</option>
<option>Frontend Developer</option>
<option>Full Stack Developer</option>
<option>Data Analyst</option>
<option>DevOps Engineer</option>
</optgroup>
<optgroup label="Non-IT Jobs">
<option>HR Executive</option>
<option>Recruiter</option>
<option>Marketing Executive</option>
<option>Sales Executive</option>
<option>Accountant</option>
</optgroup>
</select>
</div>

<div class="col-md-3 mb-3">
<label>Country</label>
<input name="country" class="form-control" required>
</div>

<div class="col-md-3 mb-3">
<label>State</label>
<input name="state" class="form-control" required>
</div>

<div class="col-md-3 mb-3">
<label>District</label>
<input name="district" class="form-control" required>
</div>

<div class="col-md-3 mb-3">
<label>Area</label>
<input name="area" class="form-control">
</div>

<div class="col-md-12 mb-3">
<label>Resume (Text / PDF converted text)</label>
<input type="file" name="resume" class="form-control" required>
</div>
</div>

<button class="btn btn-primary w-100">Submit Application</button>
</form>
</div>
</div>
</body>
</html>
"""

ADMIN_HTML = """
<!doctype html>
<html>
<head>
<title>Admin Dashboard</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<div class="container mt-4">
<h3>Admin Dashboard</h3>
<p>Total Applications: <b>{{ total }}</b> |
Average AI Score: <b>{{ avg_score }}</b></p>

<table class="table table-bordered table-striped">
<thead class="table-dark">
<tr>
<th>Name</th>
<th>Phone</th>
<th>Email</th>
<th>Job</th>
<th>Score</th>
<th>Applied At</th>
</tr>
</thead>
<tbody>
{% for a in applications %}
<tr>
<td>{{ a.name }}</td>
<td>{{ a.phone }}</td>
<td>{{ a.email }}</td>
<td>{{ a.job_role }}</td>
<td>{{ a.ai_score }}</td>
<td>{{ a.applied_at }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>
</body>
</html>
"""

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
