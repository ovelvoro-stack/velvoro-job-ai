import os, csv, smtplib
from flask import Flask, request, render_template_string
from email.mime.text import MIMEText
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

DATA_FILE = "applications.csv"

# =====================
# JOB ROLES
# =====================
IT_ROLES = [
    "Software Engineer","Backend Developer","Frontend Developer",
    "Full Stack Developer","DevOps Engineer","Cloud Engineer",
    "Data Analyst","Data Scientist","QA / Tester","Mobile App Developer"
]

NON_IT_ROLES = [
    "HR Executive","Recruiter","Sales Executive","Marketing Executive",
    "Digital Marketing Executive","Customer Support",
    "Operations Executive","Accountant","Content Writer"
]

# =====================
# QUESTIONS
# =====================
IT_QUESTIONS = [
    "Explain a system you designed or worked on.",
    "Which technologies do you use most and why?",
    "How do you approach performance or scalability issues?"
]

NON_IT_QUESTIONS = [
    "Describe your previous work experience.",
    "How do you handle pressure or targets?",
    "Why are you suitable for this role?"
]

# =====================
# CSV INIT
# =====================
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            "name","phone","email","job_role","experience",
            "country","state","district","area",
            "q1","q2","q3","ai_score","result"
        ])

# =====================
# AI SCORING (SAFE)
# =====================
def score_resume(text):
    return min(100, 50 + len(text) % 50)

# =====================
# EMAIL (SAFE)
# =====================
def send_email(to_email, name, role):
    user = os.getenv("SMTP_USER")
    pwd = os.getenv("SMTP_PASS")
    if not user or not pwd:
        return
    msg = MIMEText(f"""
Dear {name},

Thank you for applying for the {role} position at Velvoro Software Solution.

Our recruitment team will review your profile.

Regards,
Velvoro HR Team
""")
    msg["Subject"] = "Application Received – Velvoro Job AI"
    msg["From"] = user
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(user, pwd)
        s.send_message(msg)

# =====================
# ROUTES
# =====================
@app.route("/", methods=["GET","POST"])
def index():
    result = None
    if request.method == "POST":
        f = request.form
        resume = request.files.get("resume")
        text = ""
        if resume:
            path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(resume.filename))
            resume.save(path)
            text = resume.filename

        ai_score = score_resume(text + f["q1"] + f["q2"] + f["q3"])
        result = "Qualified" if ai_score >= 60 else "Not Qualified"

        with open(DATA_FILE, "a", newline="", encoding="utf-8") as fp:
            csv.writer(fp).writerow([
                f["name"],f["phone"],f["email"],f["job_role"],f["experience"],
                f["country"],f["state"],f["district"],f["area"],
                f["q1"],f["q2"],f["q3"],ai_score,result
            ])

        send_email(f["email"], f["name"], f["job_role"])

    return render_template_string(TEMPLATE,
        it_roles=IT_ROLES,
        non_it_roles=NON_IT_ROLES,
        it_q=IT_QUESTIONS,
        non_it_q=NON_IT_QUESTIONS,
        result=result
    )

@app.route("/admin")
def admin():
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return render_template_string(ADMIN_TEMPLATE, rows=rows)

# =====================
# TEMPLATES
# =====================
TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Velvoro Job AI</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<script>
const IT = {{ it_q|tojson }};
const NONIT = {{ non_it_q|tojson }};
function updateQuestions(){
  let role=document.getElementById("job_role").value;
  let qs = role && {{ it_roles|tojson }}.includes(role) ? IT : NONIT;
  for(let i=0;i<3;i++){
    document.getElementById("ql"+(i+1)).innerText=qs[i];
  }
}
</script>
</head>
<body class="container py-4">
<h3 class="mb-3">Apply for a Job</h3>

<form method="post" enctype="multipart/form-data">
<input name="name" class="form-control mb-2" placeholder="Full Name" required>
<input name="phone" class="form-control mb-2" placeholder="Phone" required>
<input name="email" class="form-control mb-2" placeholder="Email" required>

<input list="roles" id="job_role" name="job_role" class="form-control mb-2"
 placeholder="Select Job Role" onchange="updateQuestions()" required>
<datalist id="roles">
{% for r in it_roles %}<option value="{{r}}">{% endfor %}
{% for r in non_it_roles %}<option value="{{r}}">{% endfor %}
</datalist>

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

<input type="file" name="resume" class="form-control mb-3" required>
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
<tr><th>Name</th><th>Email</th><th>Job</th><th>Score</th><th>Result</th></tr>
{% for r in rows %}
<tr>
<td>{{r.name}}</td><td>{{r.email}}</td>
<td>{{r.job_role}}</td><td>{{r.ai_score}}</td><td>{{r.result}}</td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""

if __name__ == "__main__":
    app.run()
