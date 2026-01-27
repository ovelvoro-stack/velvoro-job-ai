# ============================================================
# Velvoro Job AI — FINAL app.py
# ONLY requested changes implemented
# UI / flow / CSV / email / admin / experience logic unchanged
# ============================================================

import os
import csv
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, render_template_string
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

DATA_FILE = "applications.csv"

# ============================================================
# IT JOB ROLES — A–Z FULL CADRE (LOW → HIGH, INDUSTRY-USED)
# ============================================================
IT_JOBS = [
    # Fresher / Trainee
    "Computer Operator","IT Support Trainee","Software Trainee","QA Trainee",
    "Junior IT Support Engineer","Junior Software Developer","Junior Web Developer",
    "Junior QA Tester","Junior Network Engineer",

    # Junior / Mid
    "Software Developer","Software Engineer","Backend Developer","Frontend Developer",
    "Full Stack Developer","Web Developer","Mobile App Developer",
    "Android Developer","iOS Developer","QA Engineer","Automation Engineer",
    "System Engineer","Network Engineer","Cloud Engineer","DevOps Engineer",
    "Security Engineer","Database Administrator","Data Analyst","Business Analyst",

    # Senior
    "Senior Software Engineer","Senior Backend Developer","Senior Frontend Developer",
    "Senior Full Stack Developer","Senior QA Engineer","Senior DevOps Engineer",
    "Senior Cloud Engineer","Senior Security Engineer","Senior Data Analyst",

    # Lead
    "Technical Lead","Team Lead – Software","QA Lead","DevOps Lead",
    "Cloud Lead","Data Lead","Engineering Lead",

    # Architect
    "Solution Architect","Technical Architect","Cloud Architect",
    "Data Architect","Enterprise Architect","Security Architect",

    # Manager
    "Engineering Manager","IT Manager","Delivery Manager",
    "Program Manager","Project Manager","Infrastructure Manager",

    # Director / CXO
    "Director of Engineering","Head of IT","VP Engineering",
    "Chief Technology Officer","Chief Information Officer"
]

# ============================================================
# NON-IT JOB ROLES — A–Z FULL CADRE (LOW → HIGH)
# ============================================================
NON_IT_JOBS = [
    # Entry
    "Office Assistant","Back Office Executive","Customer Support Executive",
    "Telecaller","Junior Accountant","Field Executive","Operations Assistant",
    "Admin Assistant","Store Assistant",

    # Executive
    "Sales Executive","Marketing Executive","HR Executive",
    "Recruitment Executive","Accounts Executive",
    "Digital Marketing Executive","Content Writer",
    "Relationship Executive","Business Development Executive",
    "Customer Relationship Executive",

    # Manager
    "Sales Manager","Marketing Manager","HR Manager",
    "Accounts Manager","Operations Manager",
    "Customer Support Manager","Regional Sales Manager",
    "Branch Manager","Area Sales Manager",

    # Senior Manager
    "Senior Sales Manager","Senior HR Manager",
    "Senior Operations Manager","Finance Manager",

    # Head / VP / CXO
    "Head of Sales","Head of Marketing","Head of HR",
    "Head of Operations","Finance Controller",
    "Vice President – Sales","Vice President – Operations",
    "Chief Operating Officer","Chief Financial Officer"
]

# ============================================================
# CADRE-WISE QUESTIONS (STRICTLY DIFFERENT)
# ============================================================
IT_QUESTIONS_BY_LEVEL = {
    "fresher": [
        "What core IT or programming skills have you learned so far?",
        "Explain a small project or lab work you have done.",
        "How do you approach learning new technical concepts?"
    ],
    "mid": [
        "Describe a real project you worked on and your contribution.",
        "Which tools, frameworks, or technologies do you use daily?",
        "How do you debug and resolve technical issues?"
    ],
    "senior": [
        "Explain a complex system or feature you designed or improved.",
        "How do you ensure scalability, security, and performance?",
        "How do you mentor or review work of junior engineers?"
    ],
    "lead": [
        "How do you make technical decisions for your team?",
        "Describe a challenge you faced while leading engineers.",
        "How do you balance delivery speed with code quality?"
    ],
    "architect": [
        "How do you design scalable and fault-tolerant architectures?",
        "How do you choose technologies for long-term systems?",
        "Describe an architecture decision you defended successfully."
    ],
    "manager": [
        "How do you align engineering goals with business objectives?",
        "How do you manage team performance and delivery risks?",
        "How do you communicate with stakeholders and leadership?"
    ]
}

NON_IT_QUESTIONS_BY_LEVEL = {
    "entry": [
        "Explain your understanding of this role and its responsibilities.",
        "How do you handle routine work pressure or targets?",
        "Why are you interested in this position?"
    ],
    "executive": [
        "Describe your daily responsibilities in your previous role.",
        "How do you achieve targets or KPIs?",
        "How do you handle customer or stakeholder communication?"
    ],
    "manager": [
        "How do you manage teams and track performance?",
        "Describe a challenging situation you handled successfully.",
        "How do you align your team with business goals?"
    ],
    "head": [
        "How do you define long-term strategy for your department?",
        "How do you manage senior stakeholders and large teams?",
        "Describe a major business decision you led."
    ]
}

# ============================================================
# LEVEL DETECTION (SAFE FALLBACK)
# ============================================================
def detect_it_level(role):
    r = role.lower()
    if any(x in r for x in ["trainee","junior","support","operator"]):
        return "fresher"
    if "senior" in r:
        return "senior"
    if "lead" in r:
        return "lead"
    if "architect" in r:
        return "architect"
    if any(x in r for x in ["manager","head","director","cto","cio","vp"]):
        return "manager"
    return "mid"

def detect_nonit_level(role):
    r = role.lower()
    if any(x in r for x in ["assistant","junior","executive","telecaller"]):
        return "entry"
    if "manager" in r:
        return "manager"
    if any(x in r for x in ["head","vp","chief"]):
        return "head"
    return "executive"

# ============================================================
# CSV INIT (UNCHANGED)
# ============================================================
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "name","phone","email","category","job_role","experience",
            "country","state","district","area",
            "q1","q2","q3"
        ])

# ============================================================
# EMAIL (UNCHANGED)
# ============================================================
def send_email(to_email, name, role):
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    if not smtp_user or not smtp_pass:
        return
    msg = MIMEText(
        f"""Dear {name},

Thank you for applying for the {role} position at Velvoro Software Solution.

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

# ============================================================
# ROUTES (FLOW UNCHANGED)
# ============================================================
@app.route("/", methods=["GET","POST"])
def index():
    questions = []
    if request.method == "POST":
        category = request.form["job_category"]
        role = request.form["job_role"]

        if category == "IT Jobs":
            level = detect_it_level(role)
            questions = IT_QUESTIONS_BY_LEVEL[level]
        else:
            level = detect_nonit_level(role)
            questions = NON_IT_QUESTIONS_BY_LEVEL[level]

        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                request.form["name"],request.form["phone"],
                request.form["email"],category,role,
                request.form["experience"],
                request.form.get("country",""),
                request.form.get("state",""),
                request.form.get("district",""),
                request.form.get("area",""),
                request.form.get("q1",""),
                request.form.get("q2",""),
                request.form.get("q3","")
            ])

        send_email(request.form["email"], request.form["name"], role)

    return render_template_string(
        TEMPLATE,
        it_jobs=IT_JOBS,
        non_it_jobs=NON_IT_JOBS,
        questions=questions
    )

@app.route("/admin")
def admin():
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return render_template_string(ADMIN_TEMPLATE, rows=rows)

# ============================================================
# TEMPLATES (UNCHANGED STRUCTURE)
# ============================================================
TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Velvoro Job AI</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<script>
const IT_JOBS={{it_jobs|tojson}};
const NON_IT_JOBS={{non_it_jobs|tojson}};
function loadRoles(){
  let c=document.getElementById("job_category").value;
  let r=document.getElementById("job_role");
  r.innerHTML="";
  let list=c==="IT Jobs"?IT_JOBS:NON_IT_JOBS;
  list.forEach(j=>{
    let o=document.createElement("option");
    o.value=j;o.text=j;r.appendChild(o);
  });
}
</script>
</head>
<body class="container py-4">
<h3>Velvoro Job AI</h3>
<form method="post">
<input name="name" class="form-control mb-2" placeholder="Full Name" required>
<input name="phone" class="form-control mb-2" placeholder="Phone" required>
<input name="email" class="form-control mb-2" placeholder="Email" required>

<label>Apply Job Category</label>
<select name="job_category" id="job_category" class="form-control mb-2" onchange="loadRoles()" required>
<option value="">Select</option>
<option>IT Jobs</option>
<option>Non-IT Jobs</option>
</select>

<select name="job_role" id="job_role" class="form-control mb-2" required></select>

<label>Experience (0 – 30 Years)</label>
<select name="experience" class="form-control mb-2">
{% for i in range(31) %}<option>{{i}}</option>{% endfor %}
</select>

{% for q in questions %}
<label class="fw-bold">{{q}}</label>
<textarea name="q{{loop.index}}" class="form-control mb-2" required></textarea>
{% endfor %}

<button class="btn btn-primary">Submit</button>
</form>
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
<tr><th>Name</th><th>Email</th><th>Category</th><th>Role</th><th>Exp</th></tr>
{% for r in rows %}
<tr>
<td>{{r.name}}</td><td>{{r.email}}</td><td>{{r.category}}</td>
<td>{{r.job_role}}</td><td>{{r.experience}}</td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""

if __name__=="__main__":
    app.run(debug=True)
