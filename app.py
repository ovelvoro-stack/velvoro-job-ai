import os
import csv
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, render_template_string

app = Flask(__name__)

DATA_FILE = "applications.csv"

# ------------------------
# JOB ROLES (A–Z, PRACTICAL, EXHAUSTIVE)
# ------------------------

IT_JOBS = [
    "Application Support Engineer","AI Engineer","Android Developer","Backend Developer",
    "Blockchain Developer","Business Analyst","Cloud Architect","Cloud Engineer",
    "Computer Operator","Data Analyst","Data Engineer","Data Scientist",
    "Database Administrator","DevOps Engineer","Desktop Support Engineer",
    "Firmware Engineer","Frontend Developer","Full Stack Developer",
    "Game Developer","IT Support Engineer","ML Engineer","Mobile App Developer",
    "Network Engineer","QA Engineer","QA Tester","Security Engineer",
    "Site Reliability Engineer","Software Developer","Software Engineer",
    "Systems Engineer","Tech Lead","Technical Architect",
    "UI UX Designer","Web Developer","Engineering Manager",
    "IT Manager","Head of Engineering","CTO"
]

NON_IT_JOBS = [
    "Account Executive","Account Manager","Admin Assistant","Admin Manager",
    "Area Sales Manager","Assistant Manager","Branch Manager","Business Development Executive",
    "Business Development Manager","Call Center Executive","Customer Support Executive",
    "Customer Support Manager","Digital Marketing Executive","Digital Marketing Manager",
    "Finance Executive","Finance Manager","HR Executive","HR Manager",
    "HR Business Partner","Inside Sales Executive","Key Account Manager",
    "Marketing Executive","Marketing Manager","Office Administrator",
    "Operations Executive","Operations Manager","Product Manager",
    "Project Coordinator","Project Manager","Regional Manager",
    "Relationship Manager","Sales Executive","Sales Manager",
    "Senior Manager","Store Manager","Territory Sales Executive",
    "Training Manager","Vice President","Head of Operations"
]

# ------------------------
# QUESTIONS (CADRE-WISE LOGIC)
# ------------------------

IT_QUESTIONS_BY_LEVEL = {
    "fresher": [
        "Explain the basics of technologies you have learned relevant to this role.",
        "How do you approach learning new tools or frameworks?",
        "Describe a small project or assignment you have worked on."
    ],
    "mid": [
        "Explain a real-world problem you solved using your technical skills.",
        "Which tools or frameworks do you use daily and why?",
        "How do you debug and fix production issues?"
    ],
    "senior": [
        "Describe a complex system you designed or improved.",
        "How do you ensure performance and scalability in your work?",
        "How do you mentor junior engineers?"
    ],
    "lead": [
        "How do you design technical architecture for large systems?",
        "How do you handle cross-team technical dependencies?",
        "Describe a leadership challenge you faced and solved."
    ],
    "manager": [
        "How do you balance technical decisions with business needs?",
        "How do you manage and grow engineering teams?",
        "How do you ensure timely delivery of projects?"
    ]
}

NON_IT_QUESTIONS_BY_LEVEL = {
    "entry": [
        "Describe your understanding of this role and its responsibilities.",
        "How do you handle basic work pressure or targets?",
        "Why are you interested in this position?"
    ],
    "executive": [
        "Describe your day-to-day responsibilities in your previous role.",
        "How do you achieve targets or KPIs?",
        "How do you communicate with customers or stakeholders?"
    ],
    "manager": [
        "How do you manage teams and track performance?",
        "Describe a challenging situation you handled successfully.",
        "How do you align your team with business goals?"
    ],
    "head": [
        "How do you define strategy for your department?",
        "How do you manage large teams and senior stakeholders?",
        "Describe a major business decision you led."
    ]
}

def detect_it_level(role):
    r = role.lower()
    if any(x in r for x in ["support","trainee","junior","operator"]):
        return "fresher"
    if any(x in r for x in ["senior","architect","lead","principal"]):
        return "lead"
    if any(x in r for x in ["manager","head","cto"]):
        return "manager"
    return "mid"

def detect_nonit_level(role):
    r = role.lower()
    if any(x in r for x in ["assistant","executive","coordinator"]):
        return "entry"
    if any(x in r for x in ["manager","lead"]):
        return "manager"
    if any(x in r for x in ["head","vp","director"]):
        return "head"
    return "executive"

# ------------------------
# CSV INIT
# ------------------------

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "name","phone","email","category","job_role","experience",
            "country","state","district","area",
            "q1","q2","q3"
        ])

# ------------------------
# EMAIL
# ------------------------

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

# ------------------------
# ROUTES
# ------------------------

@app.route("/", methods=["GET","POST"])
def index():
    questions = []
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        category = request.form["job_category"]
        role = request.form["job_role"]
        experience = request.form["experience"]
        country = request.form.get("country","")
        state = request.form.get("state","")
        district = request.form.get("district","")
        area = request.form.get("area","")

        if category == "IT Jobs":
            level = detect_it_level(role)
            questions = IT_QUESTIONS_BY_LEVEL.get(level, IT_QUESTIONS_BY_LEVEL["mid"])
        else:
            level = detect_nonit_level(role)
            questions = NON_IT_QUESTIONS_BY_LEVEL.get(level, NON_IT_QUESTIONS_BY_LEVEL["executive"])

        q1 = request.form.get("q1","")
        q2 = request.form.get("q2","")
        q3 = request.form.get("q3","")

        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                name,phone,email,category,role,experience,
                country,state,district,area,
                q1,q2,q3
            ])

        send_email(email, name, role)

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

# ------------------------
# TEMPLATES
# ------------------------

TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Velvoro Job AI</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<script>
const IT_JOBS = {{ it_jobs | tojson }};
const NON_IT_JOBS = {{ non_it_jobs | tojson }};

function loadRoles() {
    const cat = document.getElementById("job_category").value;
    const roleSelect = document.getElementById("job_role");
    roleSelect.innerHTML = "";
    let roles = cat === "IT Jobs" ? IT_JOBS : NON_IT_JOBS;
    roles.forEach(r=>{
        let o=document.createElement("option");
        o.value=r; o.text=r;
        roleSelect.appendChild(o);
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
<option value="">Select Category</option>
<option>IT Jobs</option>
<option>Non-IT Jobs</option>
</select>

<label>Job Role</label>
<select name="job_role" id="job_role" class="form-control mb-2" required></select>

<label>Experience (0 – 30 Years)</label>
<select name="experience" class="form-control mb-2">
{% for i in range(31) %}<option>{{i}}</option>{% endfor %}
</select>

<input name="country" class="form-control mb-2" placeholder="Country">
<input name="state" class="form-control mb-2" placeholder="State">
<input name="district" class="form-control mb-2" placeholder="District">
<input name="area" class="form-control mb-2" placeholder="Area">

{% if questions %}
{% for q in questions %}
<label class="fw-bold">{{q}}</label>
<textarea name="q{{loop.index}}" class="form-control mb-2" required></textarea>
{% endfor %}
{% endif %}

<button class="btn btn-primary">Submit</button>
</form>
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
<th>Name</th><th>Email</th><th>Category</th><th>Job</th><th>Experience</th>
</tr>
{% for r in rows %}
<tr>
<td>{{r.name}}</td>
<td>{{r.email}}</td>
<td>{{r.category}}</td>
<td>{{r.job_role}}</td>
<td>{{r.experience}}</td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
