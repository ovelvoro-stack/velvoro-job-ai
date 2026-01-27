from flask import Flask, render_template_string, request, redirect, url_for
import csv, os, uuid
from datetime import datetime
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

DATA_FILE = "applications.csv"

# =========================
# SaaS Plans (Architecture)
# =========================
DEFAULT_PLAN = "FREE"  # FREE / PRO / ENTERPRISE

PLAN_LIMITS = {
    "FREE": 20,
    "PRO": 200,
    "ENTERPRISE": 10_000
}

# =========================
# Location Dataset (Upgradeable)
# =========================
LOCATION_DATA = {
    "India": {
        "Telangana": ["Hyderabad", "Rangareddy"],
        "Karnataka": ["Bangalore Urban", "Mysore"]
    },
    "USA": {
        "California": ["Los Angeles", "San Francisco"],
        "Texas": ["Austin", "Dallas"]
    }
}

# =========================
# Job Questions
# =========================
IT_QUESTIONS = [
    "Explain your experience with backend or frontend technologies.",
    "How do you handle debugging and performance issues?",
    "Describe a project where you solved a complex technical problem."
]

NON_IT_QUESTIONS = [
    "How do you handle communication with clients or teams?",
    "Describe a situation where you solved a workplace challenge.",
    "How do you manage deadlines and work pressure?"
]

# =========================
# CSV Init
# =========================
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id","name","phone","email","job_role","experience",
            "country","state","district","area",
            "ai_score","qualification","plan","created_at"
        ])

# =========================
# Email (Plugin Ready)
# =========================
def send_confirmation_email(name, email, job):
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_pass = os.getenv("SMTP_PASSWORD")

    if not smtp_email or not smtp_pass:
        return  # Safe fallback

    msg = EmailMessage()
    msg["Subject"] = "Application Received – Velvoro Software Solution"
    msg["From"] = smtp_email
    msg["To"] = email
    msg.set_content(
        f"""Dear {name},

Thank you for applying for the {job} role at Velvoro Software Solution.

Our team has received your application successfully.

Regards,
Velvoro Software Solution"""
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(smtp_email, smtp_pass)
        server.send_message(msg)

# =========================
# AI Scoring (Safe)
# =========================
def ai_score_resume(text):
    # ENV key optional
    return min(100, max(40, len(text) % 100))

# =========================
# Qualification Logic
# =========================
def qualification(ai_score):
    return "Qualified" if ai_score >= 60 else "Not Qualified"

# =========================
# Routes
# =========================
@app.route("/", methods=["GET","POST"])
def apply():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        job_role = request.form["job_role"]
        experience = request.form["experience"]
        country = request.form["country"]
        state = request.form["state"]
        district = request.form["district"]
        area = request.form["area"]

        resume = request.files["resume"]
        resume_text = resume.filename if resume else ""

        ai_score = ai_score_resume(resume_text)
        result = qualification(ai_score)

        with open(DATA_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                str(uuid.uuid4()), name, phone, email, job_role,
                experience, country, state, district, area,
                ai_score, result, DEFAULT_PLAN,
                datetime.utcnow().isoformat()
            ])

        send_confirmation_email(name, email, job_role)

        return f"<h3>{result}</h3><p>AI Score: {ai_score}</p>"

    return render_template_string("""
<!doctype html>
<html>
<head>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5">
<div class="card p-4 shadow">
<h3>Velvoro Job Application</h3>
<form method="post" enctype="multipart/form-data">
<input name="name" class="form-control mb-2" placeholder="Name" required>
<input name="phone" class="form-control mb-2" placeholder="Phone" required>
<input name="email" class="form-control mb-2" placeholder="Email" required>

<select name="job_role" class="form-select mb-2">
<option>IT - Software Engineer</option>
<option>IT - Data Analyst</option>
<option>Non-IT - HR Executive</option>
<option>Non-IT - Marketing Executive</option>
</select>

<select name="experience" class="form-select mb-2">
{% for i in range(0,31) %}
<option>{{i}}</option>
{% endfor %}
</select>

<input name="country" class="form-control mb-2" placeholder="Country" required>
<input name="state" class="form-control mb-2" placeholder="State" required>
<input name="district" class="form-control mb-2" placeholder="District" required>
<input name="area" class="form-control mb-2" placeholder="Area" required>

<input type="file" name="resume" class="form-control mb-3" required>

<button class="btn btn-primary w-100">Submit</button>
</form>
</div>
</div>
</body>
</html>
""")

@app.route("/admin")
def admin():
    rows = []
    with open(DATA_FILE) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total = len(rows)
    avg_score = round(sum(int(r["ai_score"]) for r in rows)/total,2) if total else 0
    qualified = sum(1 for r in rows if r["qualification"]=="Qualified")

    return render_template_string("""
<h2>Admin Dashboard</h2>
<p>Total: {{total}}</p>
<p>Avg AI Score: {{avg}}</p>
<p>Qualified: {{qualified}}</p>

<table border=1>
<tr>
<th>Name</th><th>Email</th><th>Job</th><th>Score</th><th>Result</th>
</tr>
{% for r in rows %}
<tr>
<td>{{r.name}}</td><td>{{r.email}}</td>
<td>{{r.job_role}}</td><td>{{r.ai_score}}</td>
<td>{{r.qualification}}</td>
</tr>
{% endfor %}
</table>
""", rows=rows, total=total, avg=avg_score, qualified=qualified)

if __name__ == "__main__":
    app.run()
