import os
import csv
import uuid
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, render_template_string, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

DATA_FILE = "applications.csv"

# ------------------------
# QUESTIONS CONFIG
# ------------------------
IT_QUESTIONS = [
    "Explain your backend architecture experience.",
    "Which programming languages and frameworks have you worked with?",
    "How do you handle performance and scalability?"
]

NON_IT_QUESTIONS = [
    "Describe your previous work experience.",
    "How do you handle pressure and deadlines?",
    "Why should we hire you for this role?"
]

# ------------------------
# CSV INIT
# ------------------------
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "name","phone","email","job_role","experience",
            "country","state","district","area",
            "q1","q2","q3",
            "ai_score","result"
        ])

# ------------------------
# AI SCORING (SAFE)
# ------------------------
def score_resume(text):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return 50
    # placeholder for real OpenAI call
    return min(100, 60 + len(text) % 40)

# ------------------------
# EMAIL (SAFE)
# ------------------------
def send_email(to_email, name, role):
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    if not smtp_user or not smtp_pass:
        return
    msg = MIMEText(
        f"""Dear {name},

Thank you for applying for the {role} position at Velvoro Software Solution.

Our team will review your application.

Regards,
Velvoro HR Team
"""
    )
    msg["Subject"] = "Application Received – Velvoro"
    msg["From"] = smtp_user
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)

# ------------------------
# ROUTES
# ------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        job_role = request.form.get("job_role")
        experience = request.form.get("experience")
        country = request.form.get("country")
        state = request.form.get("state")
        district = request.form.get("district")
        area = request.form.get("area")

        q1 = request.form.get("q1","")
        q2 = request.form.get("q2","")
        q3 = request.form.get("q3","")

        resume = request.files.get("resume")
        resume_text = ""
        if resume:
            filename = secure_filename(resume.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            resume.save(path)
            resume_text = filename

        ai_score = score_resume(resume_text + q1 + q2 + q3)
        result = "Qualified" if ai_score >= 60 else "Not Qualified"

        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                name,phone,email,job_role,experience,
                country,state,district,area,
                q1,q2,q3,
                ai_score,result
            ])

        send_email(email, name, job_role)

    return render_template_string(TEMPLATE,
        it_questions=IT_QUESTIONS,
        non_it_questions=NON_IT_QUESTIONS,
        result=result
    )

@app.route("/admin")
def admin():
    rows = []
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return render_template_string(ADMIN_TEMPLATE, rows=rows)

# ------------------------
# TEMPLATES
# ------------------------
TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Velvoro Job AI</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<script>
function loadQuestions() {
    const role = document.getElementById("job_role").value;
    const it = {{ it_questions | tojson }};
    const nonit = {{ non_it_questions | tojson }};
    let qs = role.includes("Developer") ? it : nonit;
    for (let i=0;i<3;i++){
        document.getElementById("ql"+(i+1)).innerText = qs[i];
    }
}
</script>
</head>
<body class="container py-4">
<h3>Velvoro Job AI</h3>
<form method="post" enctype="multipart/form-data">
<input name="name" class="form-control mb-2" placeholder="Full Name" required>
<input name="phone" class="form-control mb-2" placeholder="Phone" required>
<input name="email" class="form-control mb-2" placeholder="Email" required>

<select name="job_role" id="job_role" class="form-control mb-2" onchange="loadQuestions()">
<option>Backend Developer</option>
<option>HR Executive</option>
</select>

<select name="experience" class="form-control mb-2">
{% for i in range(31) %}<option>{{i}}</option>{% endfor %}
</select>

<input name="country" class="form-control mb-2" placeholder="Country">
<input name="state" class="form-control mb-2" placeholder="State">
<input name="district" class="form-control mb-2" placeholder="District">
<input name="area" class="form-control mb-2" placeholder="Area">

<label id="ql1"></label>
<textarea name="q1" class="form-control mb-2"></textarea>
<label id="ql2"></label>
<textarea name="q2" class="form-control mb-2"></textarea>
<label id="ql3"></label>
<textarea name="q3" class="form-control mb-2"></textarea>

<input type="file" name="resume" class="form-control mb-3">

<button class="btn btn-primary">Submit</button>
</form>

{% if result %}
<div class="alert alert-info mt-3">Result: {{result}}</div>
{% endif %}
</body>
</html>
"""

ADMIN_TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Admin</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container py-4">
<h3>Admin Dashboard</h3>
<table class="table table-bordered">
<tr>
<th>Name</th><th>Email</th><th>Job</th><th>Score</th><th>Result</th>
</tr>
{% for r in rows %}
<tr>
<td>{{r.name}}</td>
<td>{{r.email}}</td>
<td>{{r.job_role}}</td>
<td>{{r.ai_score}}</td>
<td>{{r.result}}</td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
