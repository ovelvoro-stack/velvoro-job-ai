from flask import Flask, request, redirect, url_for, render_template_string, session
import csv
import os
import statistics
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "velvoro-secret"

DATA_FILE = "applications.csv"

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

SMTP_EMAIL = "yourmail@gmail.com"
SMTP_PASS = "your_app_password"

# ---------- UTILITIES ----------

def init_csv():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "email", "job", "score"])

def ai_score(resume):
    keywords = ["python", "java", "sql", "api", "flask", "django"]
    score = sum(10 for k in keywords if k in resume.lower())
    return min(score, 100)

def send_email(to_email, name, job):
    msg = MIMEText(
        f"""
Hello {name},

Thank you for applying for the {job} role at Velvoro Software Solution.

Our team will review your profile and get back to you.

Regards,
Velvoro HR Team
"""
    )
    msg["Subject"] = "Velvoro Job Application Confirmation"
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(SMTP_EMAIL, SMTP_PASS)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("Email error:", e)

# ---------- ROUTES ----------

@app.route("/", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        job = request.form["job"]
        resume = request.form["resume"]

        score = ai_score(resume)

        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([name, email, job, score])

        send_email(email, name, job)

        return "<h2>Application submitted successfully. Confirmation email sent.</h2>"

    return render_template_string("""
    <h1>Velvoro Job Application</h1>
    <form method="post">
        Name:<br><input name="name" required><br><br>
        Email:<br><input name="email" type="email" required><br><br>
        Job Role:<br>
        <select name="job">
            <option>Python Developer</option>
            <option>Java Developer</option>
            <option>HR Executive</option>
        </select><br><br>
        Resume (paste text):<br>
        <textarea name="resume" rows="6" cols="40"></textarea><br><br>
        <button type="submit">Apply</button>
    </form>
    """)

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["user"] == ADMIN_USER and request.form["pass"] == ADMIN_PASS:
            session["admin"] = True
            return redirect("/dashboard")
    return render_template_string("""
    <h2>Admin Login</h2>
    <form method="post">
        <input name="user" placeholder="username"><br><br>
        <input name="pass" type="password" placeholder="password"><br><br>
        <button>Login</button>
    </form>
    """)

@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    rows = []
    scores = []

    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
            scores.append(int(r["score"]))

    avg = round(statistics.mean(scores), 2) if scores else 0

    return render_template_string("""
    <h1>Velvoro Admin Dashboard</h1>
    <p>Total Applications: {{total}}</p>
    <p>Average Resume Score: {{avg}}</p>

    <table border="1" cellpadding="5">
        <tr><th>Name</th><th>Email</th><th>Job</th><th>Score</th></tr>
        {% for r in rows %}
        <tr>
            <td>{{r.name}}</td>
            <td>{{r.email}}</td>
            <td>{{r.job}}</td>
            <td>{{r.score}}</td>
        </tr>
        {% endfor %}
    </table>
    """, total=len(rows), avg=avg, rows=rows)

# ---------- START ----------

init_csv()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
