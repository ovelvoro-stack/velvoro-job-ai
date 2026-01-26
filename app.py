from flask import Flask, request, redirect, url_for, render_template_string
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# -------------------------------
# In-memory storage (simple & safe)
# -------------------------------
applications = []

# -------------------------------
# EMAIL CONFIG (SMTP)
# -------------------------------
SMTP_EMAIL = "yourmail@gmail.com"
SMTP_PASSWORD = "your_app_password"  # Gmail App Password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_confirmation_email(to_email, name, job, score):
    body = f"""
Dear {name},

Thank you for applying for the {job} position at Velvoro Software Solution.

Your resume has been reviewed by our AI system.
Resume Score: {score}/100

Our HR team will contact you if your profile matches our requirements.

Best Regards,
Velvoro HR Team
"""

    msg = MIMEText(body)
    msg["Subject"] = "Velvoro Job Application – Confirmation"
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("Email error:", e)

# -------------------------------
# Resume AI Scoring (Simple & Stable)
# -------------------------------
def resume_ai_score(resume_text, job):
    keywords = {
        "Python Developer": ["python", "flask", "django", "api"],
        "Java Developer": ["java", "spring", "hibernate"],
        "HR Recruiter": ["recruitment", "hiring", "interview"]
    }

    score = 0
    resume_text = resume_text.lower()

    for word in keywords.get(job, []):
        if word in resume_text:
            score += 25

    return min(score, 100)

# -------------------------------
# JOB APPLY PAGE
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        job = request.form["job"]
        resume = request.form["resume"]

        score = resume_ai_score(resume, job)

        applications.append({
            "name": name,
            "email": email,
            "job": job,
            "score": score
        })

        send_confirmation_email(email, name, job, score)

        return redirect(url_for("success"))

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Velvoro Job Application</title>
</head>
<body>
<h2>Velvoro Job Application</h2>
<form method="post">
Name:<br><input name="name" required><br><br>
Email:<br><input type="email" name="email" required><br><br>

Job Role:<br>
<select name="job">
<option>Python Developer</option>
<option>Java Developer</option>
<option>HR Recruiter</option>
</select><br><br>

Resume (paste text):<br>
<textarea name="resume" rows="6" cols="40" required></textarea><br><br>

<button type="submit">Apply Job</button>
</form>
</body>
</html>
""")

# -------------------------------
# SUCCESS PAGE
# -------------------------------
@app.route("/success")
def success():
    return "<h2>Application Submitted Successfully</h2><p>Check your email for confirmation.</p>"

# -------------------------------
# ADMIN DASHBOARD
# -------------------------------
@app.route("/admin")
def admin():
    total = len(applications)
    avg_score = round(sum(a["score"] for a in applications) / total, 2) if total else 0

    rows = ""
    for a in applications:
        rows += f"<tr><td>{a['name']}</td><td>{a['email']}</td><td>{a['job']}</td><td>{a['score']}</td></tr>"

    return render_template_string(f"""
<!DOCTYPE html>
<html>
<head>
<title>Admin Dashboard</title>
</head>
<body>
<h2>Velvoro Admin Dashboard</h2>

<p>Total Applications: <b>{total}</b></p>
<p>Average Resume Score: <b>{avg_score}</b></p>

<table border="1" cellpadding="5">
<tr>
<th>Name</th><th>Email</th><th>Job</th><th>Score</th>
</tr>
{rows}
</table>

</body>
</html>
""")

# NOTE:
# ❌ No app.run()
# ✅ Gunicorn will run this in production
