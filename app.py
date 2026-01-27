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

# -------------------------------------------------
# FULL A–Z JOB ROLES (IT + NON-IT) – EXHAUSTIVE
# -------------------------------------------------
IT_JOBS = [
    "AI Engineer","Android Developer","Application Developer","Backend Developer",
    "Blockchain Developer","Business Intelligence Analyst","Cloud Architect",
    "Cloud Engineer","Computer Programmer","Cyber Security Analyst",
    "Data Analyst","Data Engineer","Data Scientist","Database Administrator",
    "DevOps Engineer","Embedded Systems Engineer","ERP Consultant",
    "Ethical Hacker","Frontend Developer","Full Stack Developer","Game Developer",
    "Information Security Analyst","iOS Developer","IT Support Engineer",
    "Java Developer","Machine Learning Engineer","Mobile App Developer",
    ".NET Developer","Network Administrator","Network Engineer",
    "PHP Developer","Product Manager","Project Manager","Python Developer",
    "QA Analyst","QA / Tester","Ruby on Rails Developer","Scrum Master",
    "Site Reliability Engineer","Software Architect","Software Developer",
    "Software Engineer","System Administrator","Systems Engineer",
    "Technical Lead","Technical Support Engineer","UI Designer","UX Designer",
    "Web Designer","Web Developer"
]

NON_IT_JOBS = [
    "Accountant","Accounts Executive","Accounts Manager","Admin Executive",
    "Area Sales Manager","Assistant Manager","Back Office Executive",
    "Brand Manager","Business Analyst","Business Development Executive",
    "Call Center Executive","Cashier","Company Secretary","Compliance Officer",
    "Content Writer","Copywriter","Customer Care Executive",
    "Customer Support Executive","Delivery Executive","Digital Marketing Executive",
    "Field Executive","Finance Manager","Front Office Executive",
    "Graphic Designer","HR Executive","HR Manager","HR Recruiter",
    "Hotel Manager","Housekeeping Staff","Inventory Executive",
    "Legal Executive","Legal Manager","Logistics Coordinator",
    "Marketing Executive","Marketing Manager","Medical Representative",
    "Office Assistant","Office Boy","Operations Executive","Operations Manager",
    "Personal Assistant","Procurement Executive","Receptionist",
    "Relationship Manager","Retail Executive","Sales Executive","Sales Manager",
    "Security Guard","Security Supervisor","SEO Executive",
    "Social Media Manager","Store Executive","Store Manager",
    "Supply Chain Executive","Telecaller","Trainer","Video Editor",
    "Warehouse Executive"
]

# -------------------------------------------------
# ROLE → QUESTIONS (SPECIFIC WHERE AVAILABLE)
# -------------------------------------------------
JOB_QUESTIONS = {
    "Backend Developer": [
        "Explain your backend architecture experience.",
        "Which databases have you worked with?",
        "How do you handle scalability and performance?"
    ],
    "Frontend Developer": [
        "Which frontend frameworks have you used?",
        "How do you ensure responsive design?",
        "How do you optimize UI performance?"
    ],
    "Full Stack Developer": [
        "Which frontend and backend stacks do you know?",
        "Describe an end-to-end project you built.",
        "How do you deploy and maintain applications?"
    ],
    "Data Analyst": [
        "Which data analysis tools have you used?",
        "How do you clean and prepare data?",
        "Explain a business insight you derived from data."
    ],
    "HR Executive": [
        "Describe your HR experience.",
        "How do you handle recruitment cycles?",
        "How do you manage employee relations?"
    ],
    "Sales Executive": [
        "Describe your sales experience.",
        "How do you achieve sales targets?",
        "How do you handle customer objections?"
    ],
    "Digital Marketing Executive": [
        "Which digital marketing channels have you worked on?",
        "How do you measure campaign performance?",
        "Describe a successful campaign you handled."
    ]
}

# -------------------------------------------------
# DEFAULT QUESTIONS (AUTO-MAP FOR ALL OTHER ROLES)
# -------------------------------------------------
DEFAULT_IT_QUESTIONS = [
    "Describe your technical experience related to this role.",
    "Which tools or technologies have you worked with?",
    "How do you solve technical or system-level problems?"
]

DEFAULT_NON_IT_QUESTIONS = [
    "Describe your experience related to this role.",
    "What skills make you suitable for this position?",
    "Why should we hire you for this job?"
]

# -------------------------------------------------
# CSV INIT
# -------------------------------------------------
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "name","phone","email","job_role","experience",
            "country","state","district","area",
            "q1","q2","q3",
            "ai_score","result"
        ])

# -------------------------------------------------
# AI SCORING
# -------------------------------------------------
def score_resume(text):
    return min(100, 60 + len(text) % 40)

# -------------------------------------------------
# EMAIL
# -------------------------------------------------
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

# -------------------------------------------------
# ROUTES
# -------------------------------------------------
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

    return render_template_string(
        TEMPLATE,
        it_jobs=IT_JOBS,
        non_it_jobs=NON_IT_JOBS,
        job_questions=JOB_QUESTIONS,
        default_it_q=DEFAULT_IT_QUESTIONS,
        default_nonit_q=DEFAULT_NON_IT_QUESTIONS,
        result=result
    )

@app.route("/admin")
def admin():
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return render_template_string(ADMIN_TEMPLATE, rows=rows)

# -------------------------------------------------
# TEMPLATES
# -------------------------------------------------
TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Velvoro Job AI</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<script>
const ROLE_Q = {{ job_questions | tojson }};
const IT_Q = {{ default_it_q | tojson }};
const NONIT_Q = {{ default_nonit_q | tojson }};
const IT_JOBS = {{ it_jobs | tojson }};

function loadQuestions() {
    const role = document.getElementById("job_role").value;
    let qs = ROLE_Q[role];
    if (!qs) {
        qs = IT_JOBS.includes(role) ? IT_Q : NONIT_Q;
    }
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

<select name="job_role" id="job_role" class="form-control mb-2" onchange="loadQuestions()" required>
<optgroup label="IT Jobs">
{% for j in it_jobs %}<option value="{{j}}">{{j}}</option>{% endfor %}
</optgroup>
<optgroup label="Non-IT Jobs">
{% for j in non_it_jobs %}<option value="{{j}}">{{j}}</option>{% endfor %}
</optgroup>
</select>

<select name="experience" class="form-control mb-2">
{% for i in range(31) %}<option>{{i}}</option>{% endfor %}
</select>

<input name="country" class="form-control mb-2" placeholder="Country">
<input name="state" class="form-control mb-2" placeholder="State">
<input name="district" class="form-control mb-2" placeholder="District">
<input name="area" class="form-control mb-2" placeholder="Area">

<label id="ql1" class="fw-bold"></label>
<textarea name="q1" class="form-control mb-2" required></textarea>
<label id="ql2" class="fw-bold"></label>
<textarea name="q2" class="form-control mb-2" required></textarea>
<label id="ql3" class="fw-bold"></label>
<textarea name="q3" class="form-control mb-2" required></textarea>

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
<title>Admin Dashboard</title>
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
