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

# =========================
# IT ROLES (A–Z, INDUSTRY)
# =========================
IT_ROLES = [
    "AI Engineer","Android Developer","Application Support Engineer","AR/VR Engineer",
    "Automation Engineer","Backend Developer","Big Data Engineer","Blockchain Developer",
    "Build & Release Engineer","Business Intelligence Developer",
    "Cloud Administrator","Cloud Architect","Cloud Engineer","Computer Vision Engineer",
    "Cyber Security Analyst","Cyber Security Engineer","Data Analyst","Data Architect",
    "Data Engineer","Data Scientist","Database Administrator","DevOps Engineer",
    "Director of Engineering","Embedded Systems Engineer","ERP Consultant",
    "Frontend Developer","Full Stack Developer","Game Developer","Hardware Engineer",
    "IT Analyst","IT Consultant","IT Coordinator","IT Manager","IT Support Engineer",
    "IT Trainee","Junior Software Developer","Lead Engineer","Machine Learning Engineer",
    "Mobile App Developer","Network Administrator","Network Engineer","NOC Engineer",
    "Platform Engineer","Principal Engineer","Product Engineer","Program Manager",
    "QA Analyst","QA Engineer","Release Manager","Research Engineer","Robotics Engineer",
    "SAP Consultant","Scrum Master","Security Architect","Senior Data Analyst",
    "Senior Data Engineer","Senior Data Scientist","Senior DevOps Engineer",
    "Senior QA Engineer","Senior Software Engineer","Site Reliability Engineer",
    "Solution Architect","Software Architect","Software Engineer",
    "Systems Administrator","Systems Engineer","Tech Lead","Technical Architect",
    "Technical Program Manager","Test Automation Engineer","UI Developer",
    "UX Engineer","VP Engineering","Web Developer","CTO"
]

# =========================
# NON-IT ROLES (A–Z, INDUSTRY)
# =========================
NON_IT_ROLES = [
    "Account Executive","Account Manager","Accounts Assistant","Accounts Manager",
    "Administrative Assistant","Area Manager","Assistant Manager","Back Office Executive",
    "Banking Executive","Brand Manager","Branch Manager","Business Analyst",
    "Business Development Executive","Business Development Manager",
    "Call Center Executive","Chief Executive Officer","Chief Financial Officer",
    "Chief Human Resources Officer","Chief Marketing Officer","Client Relationship Manager",
    "Compliance Officer","Content Writer","Corporate Trainer","Customer Care Executive",
    "Customer Relationship Executive","Customer Success Manager","Digital Marketing Executive",
    "Digital Marketing Manager","District Manager","E-commerce Executive",
    "E-commerce Manager","Event Coordinator","Event Manager","Executive Assistant",
    "Facility Manager","Finance Executive","Finance Manager","Finance Head",
    "Front Office Executive","General Manager","Growth Manager","HR Executive",
    "HR Manager","HR Head","Inside Sales Executive","Key Account Manager",
    "Legal Executive","Legal Manager","Logistics Executive","Logistics Manager",
    "Marketing Executive","Marketing Manager","Marketing Head","Media Planner",
    "Operations Executive","Operations Manager","Operations Head","Office Assistant",
    "Office Manager","PR Executive","PR Manager","Product Manager","Program Coordinator",
    "Program Manager","Project Coordinator","Project Manager","Purchase Executive",
    "Purchase Manager","Quality Executive","Quality Manager","Regional Manager",
    "Relationship Manager","Retail Manager","Risk Analyst","Risk Manager",
    "Sales Executive","Sales Manager","Sales Head","Senior Manager",
    "Social Media Executive","Social Media Manager","Store Manager",
    "Supply Chain Executive","Supply Chain Manager","Talent Acquisition Executive",
    "Talent Acquisition Manager","Territory Manager","Training Executive",
    "Training Manager","Transport Manager","Vendor Manager","VP Operations","VP Sales"
]

# =========================
# ROLE QUESTIONS (UNCHANGED)
# =========================
ROLE_QUESTIONS = {}
DEFAULT_IT_QUESTIONS = [
    "Explain your technical background.",
    "Describe a technical challenge you solved.",
    "How do you keep your skills updated?"
]
DEFAULT_NON_IT_QUESTIONS = [
    "Describe your experience related to this role.",
    "How do you handle work pressure?",
    "Why should we hire you?"
]

# =========================
# CSV INIT
# =========================
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "name","phone","email","category","role","experience",
            "country","state","district","area",
            "q1","q2","q3","resume"
        ])

def send_email(to_email, name, role):
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    if not smtp_user or not smtp_pass:
        return
    msg = MIMEText(f"""Dear {name},

Thank you for applying for the {role} position at Velvoro Software Solution.

Regards,
Velvoro HR Team
""")
    msg["Subject"] = "Application Received – Velvoro"
    msg["From"] = smtp_user
    msg["To"] = to_email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)

@app.route("/", methods=["GET","POST"])
def index():
    submitted = False
    if request.method == "POST":
        data = request.form
        resume_file = request.files.get("resume")
        resume_name = ""
        if resume_file:
            resume_name = secure_filename(resume_file.filename)
            resume_file.save(os.path.join(app.config["UPLOAD_FOLDER"], resume_name))

        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                data.get("name"), data.get("phone"), data.get("email"),
                data.get("category"), data.get("role"), data.get("experience"),
                data.get("country"), data.get("state"),
                data.get("district"), data.get("area"),
                data.get("q1"), data.get("q2"), data.get("q3"),
                resume_name
            ])

        send_email(data.get("email"), data.get("name"), data.get("role"))
        submitted = True

    return render_template_string(
        TEMPLATE,
        it_roles=IT_ROLES,
        non_it_roles=NON_IT_ROLES,
        role_questions=ROLE_QUESTIONS,
        default_it=DEFAULT_IT_QUESTIONS,
        default_non_it=DEFAULT_NON_IT_QUESTIONS,
        submitted=submitted
    )

@app.route("/admin")
def admin():
    rows = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            for r in reader:
                rows.append(r)
    return render_template_string(ADMIN_TEMPLATE, headers=headers, rows=rows)

TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Velvoro Job AI</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<script>
const IT_ROLES = {{ it_roles|tojson }};
const NON_IT_ROLES = {{ non_it_roles|tojson }};
const ROLE_Q = {{ role_questions|tojson }};
const DEFAULT_IT = {{ default_it|tojson }};
const DEFAULT_NONIT = {{ default_non_it|tojson }};

function loadRoles(){
  const cat = document.getElementById("category").value;
  const roleSel = document.getElementById("role");
  roleSel.innerHTML = "";
  let roles = cat === "IT Jobs" ? IT_ROLES : NON_IT_ROLES;
  roles.forEach(r=>{
    let o=document.createElement("option");
    o.value=r; o.text=r; roleSel.add(o);
  });
  loadQuestions();
}

function loadQuestions(){
  const role = document.getElementById("role").value;
  let qs = ROLE_Q[role];
  if(!qs){
    qs = document.getElementById("category").value==="IT Jobs" ? DEFAULT_IT : DEFAULT_NONIT;
  }
  document.getElementById("ql1").innerText = qs[0];
  document.getElementById("ql2").innerText = qs[1];
  document.getElementById("ql3").innerText = qs[2];
}
</script>
</head>
<body class="container py-4">
<h3>Velvoro Job AI</h3>

{% if submitted %}
<div class="alert alert-success">Application submitted successfully.</div>
{% endif %}

<form method="post" enctype="multipart/form-data">
<input name="name" class="form-control mb-2" placeholder="Full Name" required>
<input name="phone" class="form-control mb-2" placeholder="Phone" required>
<input name="email" class="form-control mb-2" placeholder="Email" required>

<label>Apply Job Category</label>
<select id="category" name="category" class="form-control mb-2" onchange="loadRoles()" required>
<option value="">Select</option>
<option>IT Jobs</option>
<option>Non-IT Jobs</option>
</select>

<select id="role" name="role" class="form-control mb-2" onchange="loadQuestions()" required></select>

<label>Experience (0 – 30 Years)</label>
<select name="experience" class="form-control mb-2" required>
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
</body>
</html>
"""

ADMIN_TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Admin - Velvoro Job AI</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container py-4">
<h3>Applications</h3>
<table class="table table-bordered table-sm">
<thead>
<tr>
{% for h in headers %}
<th>{{ h }}</th>
{% endfor %}
</tr>
</thead>
<tbody>
{% for row in rows %}
<tr>
{% for col in row %}
<td>{{ col }}</td>
{% endfor %}
</tr>
{% endfor %}
</tbody>
</table>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
