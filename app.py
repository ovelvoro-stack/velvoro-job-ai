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

IT_ROLES = [
    "IT Trainee","Junior Software Developer","Software Engineer","Senior Software Engineer",
    "Tech Lead","Solution Architect","Engineering Manager","Director of Engineering","CTO",
    "DevOps Engineer","Senior DevOps Engineer","Cloud Architect","Data Analyst","Senior Data Analyst",
    "Data Scientist","Senior Data Scientist","AI Engineer","ML Engineer","QA Engineer","Senior QA Engineer"
]

NON_IT_ROLES = [
    "Office Assistant","Sales Executive","Senior Sales Executive","Area Sales Manager",
    "Regional Sales Manager","Sales Head","HR Executive","HR Manager","HR Head",
    "Operations Executive","Operations Manager","Operations Head",
    "Accountant","Senior Accountant","Finance Manager","Finance Head",
    "Marketing Executive","Marketing Manager","Marketing Head"
]

ROLE_QUESTIONS = {
    "Sales Executive": [
        "How do you approach a new customer for sales?",
        "How do you handle rejection or lost sales?",
        "Explain a target you achieved recently."
    ],
    "Sales Manager": [
        "How do you manage and motivate your sales team?",
        "How do you plan and track sales targets?",
        "How do you handle underperforming team members?"
    ],
    "HR Executive": [
        "How do you source candidates for open roles?",
        "How do you coordinate interviews?",
        "How do you ensure good communication with candidates?"
    ],
    "HR Manager": [
        "How do you design hiring strategies?",
        "How do you handle employee conflicts?",
        "How do you measure HR performance?"
    ],
    "Software Engineer": [
        "Which programming languages have you worked with?",
        "How do you debug production issues?",
        "Explain a challenging project you worked on."
    ],
    "Senior Software Engineer": [
        "How do you design scalable systems?",
        "How do you mentor junior developers?",
        "How do you handle technical debt?"
    ],
    "Tech Lead": [
        "How do you lead a development team?",
        "How do you make architectural decisions?",
        "How do you balance delivery and quality?"
    ],
    "CTO": [
        "How do you define long-term technology vision?",
        "How do you align tech strategy with business goals?",
        "How do you evaluate new technologies?"
    ]
}

DEFAULT_IT_QUESTIONS = [
    "Explain your technical background.",
    "Describe a technical challenge you solved.",
    "How do you keep your skills updated?"
]

DEFAULT_NON_IT_QUESTIONS = [
    "Describe your work experience related to this role.",
    "How do you handle pressure and deadlines?",
    "Why should we hire you for this position?"
]

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
        name = request.form.get("name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        category = request.form.get("category")
        role = request.form.get("role")
        experience = request.form.get("experience")
        country = request.form.get("country")
        state = request.form.get("state")
        district = request.form.get("district")
        area = request.form.get("area")
        q1 = request.form.get("q1")
        q2 = request.form.get("q2")
        q3 = request.form.get("q3")

        resume_file = request.files.get("resume")
        resume_name = ""
        if resume_file:
            resume_name = secure_filename(resume_file.filename)
            resume_file.save(os.path.join(app.config["UPLOAD_FOLDER"], resume_name))

        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                name,phone,email,category,role,experience,
                country,state,district,area,
                q1,q2,q3,resume_name
            ])

        send_email(email, name, role)
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
            headers = next(reader)
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
    o.value=r;o.text=r;roleSel.add(o);
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
<div class="alert alert-success">Your application has been submitted successfully.</div>
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
<tr>
{% for h in headers %}
<th>{{h}}</th>
{% endfor %}
</tr>
{% for r in rows %}
<tr>
{% for c in r %}
<td>{{c}}</td>
{% endfor %}
</tr>
{% endfor %}
</table>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
