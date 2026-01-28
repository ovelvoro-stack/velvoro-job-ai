import os
import csv
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, render_template_string, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

DATA_FILE = "applications.csv"

# =========================
# EXPANDED IT ROLES (A–Z)
# =========================
IT_ROLES = [
    "AI Engineer","AI Research Scientist","Android Developer","Application Support Engineer",
    "Associate Software Engineer","Automation Engineer","Backend Developer","BI Developer",
    "Blockchain Developer","Business Intelligence Analyst","Cloud Administrator","Cloud Architect",
    "Cloud Engineer","Computer Vision Engineer","Cyber Security Analyst","Data Analyst",
    "Data Architect","Data Engineer","Data Scientist","Database Administrator","DevOps Engineer",
    "Digital Transformation Lead","Embedded Systems Engineer","Engineering Manager",
    "Enterprise Architect","Firmware Engineer","Frontend Developer","Full Stack Developer",
    "Game Developer","Hardware Engineer","Head of Engineering","Information Security Manager",
    "Infrastructure Engineer","IT Analyst","IT Consultant","IT Manager","IT Support Engineer",
    "Java Developer","Junior Software Developer","Lead Software Engineer","Linux Administrator",
    "Machine Learning Engineer","Mobile Application Developer","Network Administrator",
    "Network Engineer","NLP Engineer","Platform Engineer","Principal Engineer",
    "Product Engineer","QA Analyst","QA Automation Engineer","Release Manager",
    "Research Engineer","Robotics Engineer","SAP Consultant","Scrum Master",
    "Security Engineer","Senior Software Engineer","Site Reliability Engineer",
    "Software Architect","Software Developer","Software Engineer","Solution Architect",
    "System Administrator","Systems Engineer","Technical Architect","Technical Lead",
    "Technical Program Manager","Technology Director","Test Engineer","UI Developer",
    "UX Engineer","VP Engineering","Web Developer","Windows Administrator","CTO"
]

# =========================
# EXPANDED NON-IT ROLES (A–Z)
# =========================
NON_IT_ROLES = [
    "Account Executive","Account Manager","Administrative Assistant","Area Manager",
    "Assistant Manager","Business Analyst","Business Development Executive",
    "Business Development Manager","Call Center Executive","Chief Business Officer",
    "Chief Financial Officer","Chief HR Officer","Chief Marketing Officer",
    "Chief Operating Officer","Client Relationship Manager","Compliance Officer",
    "Content Executive","Content Manager","Customer Care Executive",
    "Customer Success Manager","Digital Marketing Executive",
    "Digital Marketing Manager","Finance Analyst","Finance Executive",
    "Finance Manager","General Manager","Growth Manager","HR Executive",
    "HR Manager","HR Operations Manager","HR Recruiter","Inside Sales Executive",
    "Key Account Manager","Legal Executive","Legal Manager","Logistics Executive",
    "Logistics Manager","Marketing Analyst","Marketing Executive","Marketing Manager",
    "Operations Executive","Operations Manager","Office Administrator",
    "Office Assistant","Procurement Executive","Procurement Manager",
    "Product Manager","Program Manager","Public Relations Executive",
    "Public Relations Manager","Quality Manager","Regional Manager",
    "Relationship Executive","Relationship Manager","Risk Analyst",
    "Risk Manager","Sales Coordinator","Sales Executive","Sales Manager",
    "Senior Manager","Supply Chain Executive","Supply Chain Manager",
    "Talent Acquisition Executive","Talent Acquisition Manager",
    "Training Executive","Training Manager","VP Operations","VP Sales"
]

ROLE_QUESTIONS = {}
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
            "country","state","district","area","q1","q2","q3","resume"
        ])

def send_email(to_email, name, role):
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    if not smtp_user or not smtp_pass:
        return
    msg = MIMEText(f"Dear {name},\n\nThank you for applying for the {role} position.\n\nVelvoro HR Team")
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
        form = request.form
        resume = request.files.get("resume")
        resume_name = ""
        if resume:
            resume_name = secure_filename(resume.filename)
            resume.save(os.path.join(app.config["UPLOAD_FOLDER"], resume_name))
        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                form.get("name"),form.get("phone"),form.get("email"),
                form.get("category"),form.get("role"),form.get("experience"),
                form.get("country"),form.get("state"),
                form.get("district"),form.get("area"),
                form.get("q1"),form.get("q2"),form.get("q3"),resume_name
            ])
        send_email(form.get("email"), form.get("name"), form.get("role"))
        submitted = True

    return render_template_string(TEMPLATE,
        it_roles=IT_ROLES,
        non_it_roles=NON_IT_ROLES,
        submitted=submitted
    )

@app.route("/admin")
def admin():
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    return render_template_string(ADMIN_TEMPLATE, rows=rows)

TEMPLATE = """
<!doctype html>
<html>
<head>
<title>Velvoro Job AI</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<script>
const IT_ROLES={{it_roles|tojson}};
const NON_IT_ROLES={{non_it_roles|tojson}};
function loadRoles(){
 let cat=document.getElementById("category").value;
 let r=document.getElementById("role");
 r.innerHTML="";
 (cat==="IT Jobs"?IT_ROLES:NON_IT_ROLES).forEach(x=>{
   let o=document.createElement("option");o.value=x;o.text=x;r.add(o);
 });
}
</script>
</head>
<body class="container py-4">
<h3>Velvoro Job AI</h3>
{% if submitted %}<div class="alert alert-success">Application submitted successfully</div>{% endif %}
<form method="post" enctype="multipart/form-data">
<input name="name" class="form-control mb-2" placeholder="Full Name" required>
<input name="phone" class="form-control mb-2" placeholder="Phone" required>
<input name="email" class="form-control mb-2" placeholder="Email" required>
<select id="category" name="category" class="form-control mb-2" onchange="loadRoles()" required>
<option value="">Select</option><option>IT Jobs</option><option>Non-IT Jobs</option>
</select>
<select id="role" name="role" class="form-control mb-2" required></select>
<select name="experience" class="form-control mb-2">{% for i in range(31) %}<option>{{i}}</option>{% endfor %}</select>
<input name="country" class="form-control mb-2" placeholder="Country">
<input name="state" class="form-control mb-2" placeholder="State">
<input name="district" class="form-control mb-2" placeholder="District">
<input name="area" class="form-control mb-2" placeholder="Area">
<textarea name="q1" class="form-control mb-2" required></textarea>
<textarea name="q2" class="form-control mb-2" required></textarea>
<textarea name="q3" class="form-control mb-2" required></textarea>
<input type="file" name="resume" class="form-control mb-3" required>
<button class="btn btn-primary">Submit</button>
</form>
</body></html>
"""

ADMIN_TEMPLATE = """
<!doctype html>
<html><head><title>Admin</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head><body class="container py-4">
<h3>Applications</h3>
<table class="table table-bordered">
{% for r in rows %}
<tr>{% for c in r %}<td>{{c}}</td>{% endfor %}</tr>
{% endfor %}
</table>
</body></html>
"""

if __name__ == "__main__":
    app.run(debug=True)
