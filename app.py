from flask import Flask, request, redirect, render_template_string
import csv, os, datetime, smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

DATA_FILE = "applications.csv"

# ---------- INIT CSV ----------
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Name","Phone","Email","JobRole","Experience",
            "Country","State","District","Area",
            "Q1","Q2","Q3",
            "ResumeText","AIScore","Qualification","Date"
        ])

# ---------- QUESTIONS ----------
IT_QUESTIONS = [
    "Explain a project where you used programming to solve a real problem.",
    "How do you debug and improve application performance?",
    "What technologies are you most confident with and why?"
]

NON_IT_QUESTIONS = [
    "Describe your previous work experience related to this role.",
    "How do you handle pressure and deadlines?",
    "Why do you think you are suitable for this position?"
]

# ---------- AI SCORING ----------
def ai_score(resume_text):
    if not resume_text.strip():
        return 0
    # SAFE fallback (free plan)
    return min(100, max(10, len(resume_text) // 20))

# ---------- QUALIFICATION ----------
def qualify(a1, a2, a3):
    total = len(a1) + len(a2) + len(a3)
    return "Qualified" if total > 200 else "Not Qualified"

# ---------- EMAIL ----------
def send_email(name, email, job):
    try:
        smtp_email = os.getenv("SMTP_EMAIL")
        smtp_pass = os.getenv("SMTP_PASSWORD")
        if not smtp_email or not smtp_pass:
            return
        msg = MIMEText(f"""
Dear {name},

Thank you for applying for the {job} position at Velvoro Software Solution.

Your application has been received successfully.
Our team will review it and get back to you.

Regards,
Velvoro HR Team
""")
        msg["Subject"] = "Application Received – Velvoro Software Solution"
        msg["From"] = smtp_email
        msg["To"] = email

        server = smtplib.SMTP("smtp.gmail.com",587)
        server.starttls()
        server.login(smtp_email, smtp_pass)
        server.send_message(msg)
        server.quit()
    except:
        pass

# ---------- ROUTES ----------
@app.route("/", methods=["GET","POST"])
def apply():
    result = None
    if request.method == "POST":
        d = request.form
        q1,q2,q3 = d["q1"],d["q2"],d["q3"]
        resume = request.files["resume"]
        resume_text = resume.read().decode("utf-8","ignore")
        score = ai_score(resume_text)
        qualification = qualify(q1,q2,q3)

        with open(DATA_FILE,"a",newline="",encoding="utf-8") as f:
            csv.writer(f).writerow([
                d["name"],d["phone"],d["email"],d["job"],
                d["experience"],
                d["country"],d["state"],d["district"],d["area"],
                q1,q2,q3,
                resume_text,score,qualification,
                datetime.datetime.now()
            ])

        send_email(d["name"], d["email"], d["job"])
        result = qualification

    return render_template_string(TEMPLATE, it_q=IT_QUESTIONS, non_it_q=NON_IT_QUESTIONS, result=result)

@app.route("/admin")
def admin():
    rows=[]
    with open(DATA_FILE,encoding="utf-8") as f:
        rows=list(csv.reader(f))[1:]
    return render_template_string(ADMIN_TEMPLATE, rows=rows)

# ---------- TEMPLATES ----------
TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Velvoro Job AI</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<nav class="navbar navbar-dark bg-primary px-4">
<span class="navbar-brand">Velvoro Software Solution</span>
</nav>

<div class="container my-5">
<div class="card shadow p-4">
<h3 class="text-center mb-3">Apply for a Job</h3>

{% if result %}
<div class="alert alert-info text-center">
<strong>Result:</strong> {{result}}
</div>
{% endif %}

<form method="post" enctype="multipart/form-data">
<input class="form-control mb-2" name="name" placeholder="Full Name" required>
<input class="form-control mb-2" name="phone" placeholder="Phone Number" required>
<input class="form-control mb-2" name="email" placeholder="Email" required>

<select class="form-control mb-2" name="job" id="job" required>
<option value="">Select Job Role</option>
<option>Software Engineer</option>
<option>Backend Developer</option>
<option>HR Executive</option>
<option>Marketing Executive</option>
</select>

<select class="form-control mb-2" name="experience">
{% for i in range(0,31) %}
<option>{{i}}</option>
{% endfor %}
</select>

<input class="form-control mb-2" name="country" placeholder="Country" required>
<input class="form-control mb-2" name="state" placeholder="State" required>
<input class="form-control mb-2" name="district" placeholder="District" required>
<input class="form-control mb-2" name="area" placeholder="Area" required>

<input type="file" class="form-control mb-2" name="resume" required>

<label id="q1l"></label>
<textarea class="form-control mb-2" name="q1" required></textarea>
<label id="q2l"></label>
<textarea class="form-control mb-2" name="q2" required></textarea>
<label id="q3l"></label>
<textarea class="form-control mb-2" name="q3" required></textarea>

<button class="btn btn-primary w-100">Submit Application</button>
</form>
</div>
</div>

<script>
const it={{it_q|tojson}}, nonit={{non_it_q|tojson}};
document.getElementById("job").onchange=function(){
 let q = this.value.includes("Engineer")||this.value.includes("Developer") ? it : nonit;
 document.getElementById("q1l").innerText=q[0];
 document.getElementById("q2l").innerText=q[1];
 document.getElementById("q3l").innerText=q[2];
};
</script>
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
<body class="container my-5">
<h3>Admin Dashboard</h3>
<table class="table table-bordered">
<tr>
<th>Name</th><th>Phone</th><th>Email</th><th>Job</th>
<th>Exp</th><th>Location</th><th>Score</th><th>Status</th>
</tr>
{% for r in rows %}
<tr>
<td>{{r[0]}}</td><td>{{r[1]}}</td><td>{{r[2]}}</td>
<td>{{r[3]}}</td><td>{{r[4]}}</td>
<td>{{r[5]}},{{r[6]}},{{r[7]}},{{r[8]}}</td>
<td>{{r[13]}}</td><td>{{r[14]}}</td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""

if __name__ == "__main__":
    app.run()
