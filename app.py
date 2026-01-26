from flask import Flask, request, redirect, url_for, render_template_string
import csv
import os

app = Flask(__name__)

DATA_FILE = "applications.csv"

# Create CSV if not exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Email", "Job", "Score"])

# ---------- BASIC AI SCORE (UNCHANGED LOGIC) ----------
def calculate_score(resume_text):
    keywords = ["python", "developer", "flask", "api", "sql"]
    score = sum(1 for k in keywords if k in resume_text.lower())
    return min(score * 20, 100)

# ---------- USER PAGE ----------
@app.route("/", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        job = request.form["job"]
        resume = request.form["resume"]

        score = calculate_score(resume)

        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([name, email, job, score])

        return redirect(url_for("success"))

    return render_template_string(USER_HTML)

# ---------- SUCCESS ----------
@app.route("/success")
def success():
    return render_template_string(SUCCESS_HTML)

# ---------- ADMIN DASHBOARD ----------
@app.route("/admin")
def admin():
    applications = []
    scores = []

    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            applications.append(row)
            scores.append(int(row["Score"]))

    total = len(applications)
    avg_score = round(sum(scores) / total, 2) if total > 0 else 0

    return render_template_string(
        ADMIN_HTML,
        total=total,
        avg_score=avg_score,
        applications=applications
    )

# ---------- HTML TEMPLATES ----------

USER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Velvoro Job Application</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5">
    <div class="card shadow">
        <div class="card-header bg-primary text-white">
            <h4 class="mb-0">Velvoro Job Application</h4>
        </div>
        <div class="card-body">
            <form method="post">
                <div class="mb-3">
                    <label class="form-label">Full Name</label>
                    <input name="name" class="form-control" required>
                </div>

                <div class="mb-3">
                    <label class="form-label">Email</label>
                    <input name="email" type="email" class="form-control" required>
                </div>

                <div class="mb-3">
                    <label class="form-label">Job Role</label>
                    <select name="job" class="form-select">
                        <option>Python Developer</option>
                        <option>Java Developer</option>
                        <option>HR Recruiter</option>
                        <option>Sales Executive</option>
                    </select>
                </div>

                <div class="mb-3">
                    <label class="form-label">Resume (Paste text)</label>
                    <textarea name="resume" rows="5" class="form-control" required></textarea>
                </div>

                <button class="btn btn-primary w-100">Apply Job</button>
            </form>
        </div>
    </div>
</div>
</body>
</html>
"""

SUCCESS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Success</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5 text-center">
    <div class="alert alert-success shadow">
        <h4>Application Submitted Successfully</h4>
        <p>You will receive a confirmation email.</p>
        <a href="/" class="btn btn-outline-primary mt-2">Apply Another</a>
    </div>
</div>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5">
    <h3 class="mb-4">Velvoro Admin Dashboard</h3>

    <div class="row mb-4">
        <div class="col-md-6">
            <div class="card shadow text-center">
                <div class="card-body">
                    <h6>Total Applications</h6>
                    <h2>{{ total }}</h2>
                </div>
            </div>
        </div>

        <div class="col-md-6">
            <div class="card shadow text-center">
                <div class="card-body">
                    <h6>Average Resume Score</h6>
                    <h2>{{ avg_score }}</h2>
                </div>
            </div>
        </div>
    </div>

    <div class="card shadow">
        <div class="card-body">
            <table class="table table-bordered table-striped">
                <thead class="table-dark">
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Job</th>
                        <th>Score</th>
                    </tr>
                </thead>
                <tbody>
                {% for a in applications %}
                    <tr>
                        <td>{{ a.Name }}</td>
                        <td>{{ a.Email }}</td>
                        <td>{{ a.Job }}</td>
                        <td>{{ a.Score }}</td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
</body>
</html>
"""

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
