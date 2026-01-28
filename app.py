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

ROLE_QUESTIONS = {
    "FRESHER_IT": [
        "What basic IT or programming skills do you have?",
        "Which technologies are you currently learning?",
        "How do you approach learning new technical skills?"
    ],
    "JUNIOR_IT": [
        "Which programming languages have you worked with?",
        "How do you debug issues in your code?",
        "Describe a project you have worked on."
    ],
    "SENIOR_IT": [
        "How do you design scalable systems?",
        "How do you mentor junior developers?",
        "How do you handle technical debt?"
    ],
    "LEAD_IT": [
        "How do you lead a technical team?",
        "How do you review and approve code?",
        "How do you balance delivery and quality?"
    ],
    "ARCH_IT": [
        "How do you design system architecture?",
        "How do you choose technologies?",
        "How do you handle performance bottlenecks?"
    ],
    "MANAGER_IT": [
        "How do you manage engineering teams?",
        "How do you track project delivery?",
        "How do you handle underperformance?"
    ],
    "CXO_IT": [
        "How do you define long-term tech vision?",
        "How do you align tech with business?",
        "How do you evaluate new technologies?"
    ],
    "EXEC_NONIT": [
        "Describe your day-to-day responsibilities.",
        "How do you handle work pressure?",
        "How do you communicate with stakeholders?"
    ],
    "MANAGER_NONIT": [
        "How do you manage your team?",
        "How do you track performance?",
        "How do you resolve conflicts?"
    ],
    "HEAD_NONIT": [
        "How do you define department strategy?",
        "How do you measure success?",
        "How do you scale operations?"
    ]
}

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
        submitted=submitted
    )

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

function getQuestions(category, role){
  if(category==="IT Jobs"){
    if(role.includes("Trainee")) return ROLE_Q["FRESHER_IT"];
    if(role.includes("Junior")) return ROLE_Q["JUNIOR_IT"];
    if(role.includes("Senior")) return ROLE_Q["SENIOR_IT"];
    if(role.includes("Lead")) return ROLE_Q["LEAD_IT"];
    if(role.includes("Architect")) return ROLE_Q["ARCH_IT"];
    if(role.includes("Manager")) return ROLE_Q["MANAGER_IT"];
    return ROLE_Q["CXO_IT"];
  } else {
    if(role.includes("Executive")) return ROLE_Q["EXEC_NONIT"];
    if(role.includes("Manager")) return ROLE_Q["MANAGER_NONIT"];
    return ROLE_Q["HEAD_NONIT"];
  }
}

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
  const cat = document.getElementById("category").value;
  const role = document.getElementById("role").value;
  if(!role) return;
  const qs = getQuestions(cat, role);
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
