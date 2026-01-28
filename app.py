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
# JOB ROLES (A–Z)
# =========================
IT_ROLES = [
    "IT Trainee","Junior Software Developer","Software Engineer","Senior Software Engineer",
    "Tech Lead","Solution Architect","Engineering Manager","Director of Engineering","CTO",
    "DevOps Engineer","Senior DevOps Engineer","Cloud Architect",
    "Data Analyst","Senior Data Analyst","Data Scientist","Senior Data Scientist",
    "AI Engineer","ML Engineer","QA Engineer","Senior QA Engineer"
]

NON_IT_ROLES = [
    "Office Assistant","Call Center Executive",
    "Sales Executive","Senior Sales Executive","Area Sales Manager",
    "Regional Sales Manager","Sales Head",
    "HR Executive","HR Manager","HR Head",
    "Operations Executive","Operations Manager","Operations Head",
    "Accountant","Senior Accountant","Finance Manager","Finance Head",
    "Marketing Executive","Marketing Manager","Marketing Head"
]

# =========================
# ROLE-SPECIFIC QUESTIONS
# =========================
ROLE_QUESTIONS = {
    # IT – Fresher / Junior
    "IT Trainee": [
        "What basic IT or programming skills do you have?",
        "Which technologies are you currently learning?",
        "How do you approach learning new technical skills?"
    ],
    "Junior Software Developer": [
        "Which programming languages have you worked with?",
        "How do you debug basic coding issues?",
        "Describe a small project you worked on."
    ],

    # IT – Mid / Senior
    "Software Engineer": [
        "Which languages and frameworks do you use regularly?",
        "How do you debug production issues?",
        "Describe a challenging project you completed."
    ],
    "Senior Software Engineer": [
        "How do you design scalable systems?",
        "How do you mentor junior developers?",
        "How do you manage technical debt?"
    ],

    # IT – Lead / Architect
    "Tech Lead": [
        "How do you lead and review a development team?",
        "How do you make architectural decisions?",
        "How do you balance speed and code quality?"
    ],
    "Solution Architect": [
        "How do you design system architecture?",
        "How do you select technologies for a project?",
        "How do you handle performance bottlenecks?"
    ],
    "Cloud Architect": [
        "How do you design cloud-native architectures?",
        "How do you optimize cloud costs?",
        "How do you ensure cloud security?"
    ],

    # IT – Management
    "Engineering Manager": [
        "How do you manage engineering teams?",
        "How do you track delivery and performance?",
        "How do you handle underperforming team members?"
    ],
    "Director of Engineering": [
        "How do you align engineering with business goals?",
        "How do you scale teams and processes?",
        "How do you manage multiple projects?"
    ],
    "CTO": [
        "How do you define long-term technology vision?",
        "How do you align tech strategy with business?",
        "How do you evaluate new technologies?"
    ],

    # Non-IT – Entry / Executive
    "Office Assistant": [
        "What administrative tasks have you handled?",
        "How do you organize daily office work?",
        "How do you prioritize tasks?"
    ],
    "Call Center Executive": [
        "How do you handle customer calls?",
        "How do you deal with difficult customers?",
        "How do you achieve call targets?"
    ],
    "Sales Executive": [
        "How do you approach a new customer?",
        "How do you handle sales rejection?",
        "Describe a sales target you achieved."
    ],

    # Non-IT – Manager
    "Area Sales Manager": [
        "How do you manage a sales territory?",
        "How do you achieve regional targets?",
        "How do you motivate your team?"
    ],
    "Regional Sales Manager": [
        "How do you plan regional sales strategy?",
        "How do you track team performance?",
        "How do you expand new markets?"
    ],
    "HR Executive": [
        "How do you source candidates?",
        "How do you coordinate interviews?",
        "How do you communicate with candidates?"
    ],
    "HR Manager": [
        "How do you design hiring strategies?",
        "How do you handle employee conflicts?",
        "How do you measure HR performance?"
    ],

    # Non-IT – Head
    "Sales Head": [
        "How do you define sales strategy?",
        "How do you forecast revenue?",
        "How do you manage large sales teams?"
    ],
    "HR Head": [
        "How do you align HR with business goals?",
        "How do you build company culture?",
        "How do you plan workforce needs?"
    ],
    "Operations Head": [
        "How do you optimize operations?",
        "How do you manage operational risks?",
        "How do you improve efficiency at scale?"
    ],
    "Finance Head": [
        "How do you manage company finances?",
        "How do you control budgets and costs?",
        "How do you ensure financial compliance?"
    ],
    "Marketing Head": [
        "How do you define marketing strategy?",
        "How do you measure campaign ROI?",
        "How do you build brand presence?"
    ]
}

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

# =========================
# EMAIL
# =========================
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

# =========================
# ROUTES
# =========================
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

# =========================
# TEMPLATE
# =========================
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

if __name__ == "__main__":
    app.run(debug=True)
