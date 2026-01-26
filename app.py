from flask import Flask, request, redirect, url_for, render_template_string
import csv, os, datetime, smtplib
from email.message import EmailMessage
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "resumes"
DATA_FILE = "applications.csv"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==============================
# EMAIL CONFIG (ENV VARIABLES)
# ==============================
# Render / Local లో ఇవి Environment Variables గా పెట్టాలి
# EMAIL_USER = yourgmail@gmail.com
# EMAIL_PASS = Gmail App Password
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")

# ==============================
# JOB QUESTIONS
# ==============================
IT_QUESTIONS = [
    "Explain REST API in simple terms.",
    "What is the difference between frontend and backend?",
    "What programming language are you most comfortable with and why?"
]

NON_IT_QUESTIONS = [
    "How do you handle work pressure?",
    "Explain your communication skills.",
    "Why should we hire you for this role?"
]

# ==============================
# CSV INIT
# ==============================
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Name", "Phone", "Email", "JobRole",
            "Score", "Result", "Time"
        ])

# ==============================
# EMAIL FUNCTION
# ==============================
def send_confirmation_mail(name, email, job):
    if not EMAIL_USER or not EMAIL_PASS:
        return  # Mail config లేకపోయినా app break కాకూడదు

    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = email
    msg["Subject"] = "Velvoro Software Solution – Job Application Received"

    msg.set_content(f"""
Dear {name},

Congratulations 🎉

Thank you for applying for the position of {job}
at Velvoro Software Solution.

Our team will review your application and
get back to you shortly.

Regards,
Velvoro Software Solution
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

# ==============================
# BASIC AI SCORING LOGIC
# ==============================
def evaluate_answers(answers):
    score = 0
    for ans in answers:
        if len(ans.strip()) >= 20:
            score += 1
    return score

# ==============================
# APPLY PAGE
# ==============================
@app.route("/", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        job = request.form["job"]
        answers = [
            request.form["q1"],
            request.form["q2"],
            request.form["q3"]
        ]

        resume = request.files["resume"]
        if resume:
            filename = secure_filename(resume.filename)
            resume.save(os.path.join(UPLOAD_FOLDER, filename))

        score = evaluate_answers(answers)
        result = "Qualified" if score >= 2 else "Not Qualified"

        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                name, phone, email, job,
                score, result,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            ])

        send_confirmation_mail(name, email, job)

        return render_template_string(SUCCESS_HTML, result=result)

    return render_template_string(APPLY_HTML)

# ==============================
# ADMIN DASHBOARD
# ==============================
@app.route("/admin")
def admin():
    rows = []
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        rows = list(reader)

    return render_template_string(ADMIN_HTML, rows=rows)

# ==============================
# HTML TEMPLATES
# ==============================
APPLY_HTML = """
<!doctype html>
<html>
<head>
<title>Velvoro Job Apply</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<script>
function updateQuestions() {
    const job = document.getElementById("job").value;
    const it = ["Software Engineer","Backend Developer","Frontend Developer","Full Stack Developer"];
    let q = job.includes("Engineer") || job.includes("Developer") ? "IT" : "NONIT";

    document.getElementById("q1").placeholder = q === "IT" ? "Explain REST API" : "How do you handle pressure?";
    document.getElementById("q2").placeholder = q === "IT" ? "Frontend vs Backend?" : "Your communication skills?";
    document.getElementById("q3").placeholder = q === "IT" ? "Favourite language?" : "Why should we hire you?";
}
</script>
</head>
<body class="bg-light">
<div class="container mt-5">
<div class="card shadow p-4">
<h3 class="mb-3 text-center">Velvoro Software Solution – Job Application</h3>
<form method="post" enctype="multipart/form-data">
<input class="form-control mb-2" name="name" placeholder="Full Name" required>
<input class="form-control mb-2" name="phone" placeholder="Phone Number" required>
<input class="form-control mb-2" type="email" name="email" placeholder="Email" required>

<select class="form-control mb-2" name="job" id="job" onchange="updateQuestions()" required>
<option value="">Select Job Role</option>
<option>Software Engineer</option>
<option>Backend Developer</option>
<option>Frontend Developer</option>
<option>HR Executive</option>
<option>Marketing Executive</option>
<option>Sales Executive</option>
</select>

<input class="form-control mb-2" type="file" name="resume" required>

<textarea class="form-control mb-2" name="q1" id="q1" placeholder="Question 1" required></textarea>
<textarea class="form-control mb-2" name="q2" id="q2" placeholder="Question 2" required></textarea>
<textarea class="form-control mb-3" name="q3" id="q3" placeholder="Question 3" required></textarea>

<button class="btn btn-primary w-100">Submit Application</button>
</form>
</div>
</div>
</body>
</html>
"""

SUCCESS_HTML = """
<!doctype html>
<html>
<head>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5">
<div class="alert alert-success text-center shadow">
<h4>Application Submitted Successfully</h4>
<p>Status: <b>{{result}}</b></p>
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
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-dark text-white">
<div class="container mt-4">
<h3>Admin Dashboard</h3>
<table class="table table-dark table-striped mt-3">
<tr>
<th>Name</th><th>Phone</th><th>Email</th><th>Job</th><th>Score</th><th>Result</th><th>Time</th>
</tr>
{% for r in rows %}
<tr>
<td>{{r[0]}}</td><td>{{r[1]}}</td><td>{{r[2]}}</td>
<td>{{r[3]}}</td><td>{{r[4]}}</td><td>{{r[5]}}</td><td>{{r[6]}}</td>
</tr>
{% endfor %}
</table>
</div>
</body>
</html>
"""

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
