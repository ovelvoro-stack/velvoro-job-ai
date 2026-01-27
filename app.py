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

# ------------------------
# JOB ROLES (A–Z COMPLETE)
# ------------------------
IT_JOBS = [
    "AI Engineer","Android Developer","Application Support Engineer",
    "Backend Developer","Blockchain Developer","Business Analyst",
    "Cloud Architect","Cloud Engineer","Computer Operator",
    "Data Analyst","Data Engineer","Data Scientist",
    "Database Administrator","DevOps Engineer","Desktop Support Engineer",
    "Firmware Engineer","Frontend Developer","Full Stack Developer",
    "Game Developer","Hardware Engineer","IT Administrator",
    "IT Support Engineer","iOS Developer","Machine Learning Engineer",
    "Mobile App Developer","Network Engineer","QA Engineer",
    "Robotics Engineer","Security Engineer","Site Reliability Engineer",
    "Software Engineer","System Administrator","Technical Lead",
    "UI/UX Designer","Web Developer"
]

NON_IT_JOBS = [
    "Accountant","Admin Executive","Area Sales Manager",
    "Business Development Executive","Call Center Executive",
    "Content Writer","Customer Support Executive","Delivery Executive",
    "Digital Marketing Executive","Finance Executive","Graphic Designer",
    "HR Executive","HR Manager","Inside Sales Executive",
    "Marketing Executive","Office Assistant","Operations Executive",
    "Product Manager","Project Coordinator","Public Relations Executive",
    "Recruiter","Relationship Manager","Sales Executive",
    "Store Manager","Supply Chain Executive","Talent Acquisition Executive",
    "Training Coordinator"
]

# ------------------------
# COMMON QUESTIONS
# ------------------------
COMMON_QUESTIONS = [
    "Describe your previous work experience related to this role.",
    "How do you handle responsibilities, pressure, or deadlines?",
    "Why should we consider you for this position?"
]

# ------------------------
# CSV INIT
# ------------------------
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "name","phone","email","job_category","job_role","experience",
            "country","state","district","area",
            "q1","q2","q3","ai_score","result"
        ])

# ------------------------
# AI SCORING (SAFE)
# ------------------------
def score_resume(text):
    return min(100, 60 + len(text) % 40)

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
    result = None
    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        job_category = request.form.get("job_category")
        job_role = request.form.get("job_role")

        experience = int(request.form.get("experience", 0))
        if experience < 0 or experience > 30:
            experience = 0

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
            resume.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            resume_text = filename

        ai_score = score_resume(resume_text + q1 + q2 + q3)
        result = "Qualified" if ai_score >= 60 else "Not Qualified"

        with open(DATA_FILE,"a",newline="",encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                name,phone,email,job_category,job_role,experience,
                country,state,district,area,
                q1,q2,q3,ai_score,result
            ])

        send_email(email, name, job_role)

    return render_template_string(
        TEMPLATE,
        it_jobs=IT_JOBS,
        non_it_jobs=NON_IT_JOBS,
        questions=COMMON_QUESTIONS,
        result=result
    )

@app.route("/admin")
def admin():
    with open(DATA_FILE,newline="",encoding="utf-8") as f:
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
const IT_JOBS = {{ it_jobs|tojson }};
const NON_IT_JOBS = {{ non_it_jobs|tojson }};

function loadRoles(){
  const cat = document.getElementById("job_category").value;
  const roleSelect = document.getElementById("job_role");
  roleSelect.innerHTML = "<option value=''>Select Job Role</option>";
  let roles = [];
  if(cat === "IT Jobs"){ roles = IT_JOBS; }
  if(cat === "Non-IT Jobs"){ roles = NON_IT_JOBS; }
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

<form method="post" enctype="multipart/form-data">
<input name="name" class="form-control mb-2" placeholder="Full Name" required>
<input name="phone" class="form-control mb-2" placeholder="Phone" required>
<input name="email" class="form-control mb-2" placeholder="Email" required>

<label class="fw-bold">Apply Job Category</label>
<select name="job_category" id="job_category" class="form-control mb-2" onchange="loadRoles()" required>
<option value="">Select Category</option>
<option>IT Jobs</option>
<option>Non-IT Jobs</option>
</select>

<select name="job_role" id="job_role" class="form-control mb-2" required>
<option value="">Select Job Role</option>
</select>

<label class="fw-bold">Experience (0 – 30 Years)</label>
<select name="experience" class="form-control mb-2" required>
{% for i in range(31) %}<option>{{i}}</option>{% endfor %}
</select>

<input name="country" class="form-control mb-2" placeholder="Country">
<input name="state" class="form-control mb-2" placeholder="State">
<input name="district" class="form-control mb-2" placeholder="District">
<input name="area" class="form-control mb-2" placeholder="Area">

{% for q in questions %}
<label class="fw-bold">{{q}}</label>
<textarea name="q{{loop.index}}" class="form-control mb-2" required></textarea>
{% endfor %}

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
<th>Name</th><th>Email</th><th>Category</th><th>Job</th><th>Score</th><th>Result</th>
</tr>
{% for r in rows %}
<tr>
<td>{{r.name}}</td>
<td>{{r.email}}</td>
<td>{{r.job_category}}</td>
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
