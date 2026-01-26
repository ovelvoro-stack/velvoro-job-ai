from flask import Flask, request, redirect, url_for, render_template_string, session
import csv, os, datetime, random, smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = "velvoro_secret_key"

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

FILES = {
    "applications": f"{DATA_DIR}/applications.csv",
    "payments": f"{DATA_DIR}/payments.csv"
}

# -------------------------------
# BASIC HTML TEMPLATES (INLINE)
# -------------------------------

APPLY_HTML = """
<h2>Velvoro Job Application</h2>
<form method="post" enctype="multipart/form-data">
Name:<br><input name="name" required><br>
Phone:<br><input name="phone" required><br>
Email:<br><input name="email" required><br><br>

Category:<br>
<select name="category">
<option>IT</option>
<option>Non-IT</option>
</select><br><br>

Job Role:<br>
<select name="job">
<option>Python Developer</option>
<option>Java Developer</option>
<option>HR Recruiter</option>
<option>Sales Executive</option>
</select><br><br>

Experience:<br>
<select name="exp">
{% for i in range(0,31) %}
<option>{{i}} Years</option>
{% endfor %}
</select><br><br>

Qualification:<br>
<select name="qualification">
<option>Any Degree</option>
<option>B.Tech</option>
<option>MBA</option>
<option>Inter</option>
</select><br><br>

Resume:<br>
<input type="file" name="resume" required><br><br>

<b>Quiz</b><br>
Q1: Python is?<br>
<input type="radio" name="q1" value="correct">Programming Language<br>
<input type="radio" name="q1" value="wrong">Database<br><br>

<button type="submit">Apply Job</button>
</form>
"""

SUCCESS_HTML = """
<h2>Application Submitted Successfully</h2>
<p>You will receive confirmation email.</p>
"""

ADMIN_LOGIN = """
<h2>Admin Login</h2>
<form method="post">
<input name="username" placeholder="Username"><br>
<input name="password" type="password" placeholder="Password"><br><br>
<button>Login</button>
</form>
"""

ADMIN_DASHBOARD = """
<h2>Admin Dashboard</h2>
<p>Total Applications: {{apps}}</p>
<p>Total Revenue: ₹{{revenue}}</p>
<a href="/admin/logout">Logout</a>
"""

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------

def resume_score(filename):
    score = 50
    for k in ["python","java","sql","sales","hr"]:
        if k in filename.lower():
            score += 10
    return min(score,100)

def quiz_score(answer):
    return 1 if answer == "correct" else 0

def send_email(to, name, job):
    try:
        msg = EmailMessage()
        msg["Subject"] = "Velvoro Job Application Received"
        msg["From"] = "Velvoro <yourmail@gmail.com>"
        msg["To"] = to
        msg.set_content(f"""
Dear {name},

Your application for {job} has been received.
Our HR team will contact you.

Velvoro Software Solution
""")
        with smtplib.SMTP_SSL("smtp.gmail.com",465) as s:
            s.login("yourmail@gmail.com","APP_PASSWORD")
            s.send_message(msg)
    except:
        pass

# -------------------------------
# ROUTES
# -------------------------------

@app.route("/", methods=["GET","POST"])
def apply():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        job = request.form["job"]
        resume = request.files["resume"]

        r_score = resume_score(resume.filename)
        q_score = quiz_score(request.form.get("q1"))

        with open(FILES["applications"],"a",newline="",encoding="utf-8") as f:
            csv.writer(f).writerow([
                name, email, job, r_score, q_score, datetime.date.today()
            ])

        send_email(email, name, job)
        return redirect("/success")

    return render_template_string(APPLY_HTML)

@app.route("/success")
def success():
    return render_template_string(SUCCESS_HTML)

# -------------------------------
# ADMIN
# -------------------------------

@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            session["admin"] = True
            return redirect("/admin/dashboard")
    return render_template_string(ADMIN_LOGIN)

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    apps = 0
    revenue = 0

    if os.path.exists(FILES["applications"]):
        apps = sum(1 for _ in open(FILES["applications"],encoding="utf-8"))

    if os.path.exists(FILES["payments"]):
        for r in csv.reader(open(FILES["payments"],encoding="utf-8")):
            revenue += int(r[1])

    return render_template_string(ADMIN_DASHBOARD, apps=apps, revenue=revenue)

@app.route("/admin/logout")
def logout():
    session.clear()
    return redirect("/admin")

# -------------------------------
# PAYMENT (DUMMY PAID JOB)
# -------------------------------

@app.route("/pay")
def pay():
    amount = random.choice([299,499,999])
    with open(FILES["payments"],"a",newline="") as f:
        csv.writer(f).writerow(["Company",amount,datetime.date.today()])
    return f"Payment Successful ₹{amount}"

# -------------------------------
# MAIN
# -------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
